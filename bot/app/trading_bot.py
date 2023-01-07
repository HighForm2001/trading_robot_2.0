from spectators import BreakSpectator, ImbalanceSpectator, OrderBlockSpectator, RangeSpectator, TimeSpectator, \
    ChartSpectator
import MetaTrader5 as mt5
from tools import calculator, order
import plotly.graph_objects as go
import pandas as pd
import pathlib
import os

excel_folder = "excel"


class Bot:
    higher_timeframe: ChartSpectator = None
    lower_timeframe: ChartSpectator = None
    range_spectator: RangeSpectator = None
    time_spectator: TimeSpectator = None
    imbalance_spectator: ImbalanceSpectator = None
    orderblock_spectator: OrderBlockSpectator = None
    break_spectator: BreakSpectator = None
    reached_equilibrium = False
    current_date = None
    confirmed_trend: str = None
    equilibrium = 0
    imbalance_confirmed = False
    orderblock_confirmed = False
    bos_start_point_time: int = 0
    poi = None  # point of interest
    poi_low = poi_high = 0
    mode = "Simulation"
    initial_balance = 0  # initial balance of the user
    account_balance = 0  # account balance of the user
    point_value = 0
    pending_trade = False
    opened_trade = False
    fig_higher: go = None
    fig_lower: go = None
    trade = []
    reached_equilibrium_time = None
    file_name = ""

    def __init__(self, symbol_name, account_balance, lower_df=None, higher_df=None):
        # initialize Bot
        print("trading bot initializing")
        self.account_balance = self.initial_balance = account_balance
        self.point_value = calculator.get_point_value(symbol_name)
        # if len(lower_df) > 0 and len(higher_df) > 0:
        if lower_df is not None and higher_df is not None:
            self.higher_timeframe = ChartSpectator.ChartSpectator(symbol_name, mt5.TIMEFRAME_M5, df=higher_df)
            self.lower_timeframe = ChartSpectator.ChartSpectator(symbol_name, mt5.TIMEFRAME_M1, df=lower_df)
        else:
            # print("assigning timeframe")
            self.higher_timeframe = ChartSpectator.ChartSpectator(symbol_name, mt5.TIMEFRAME_M5)
            self.lower_timeframe = ChartSpectator.ChartSpectator(symbol_name, mt5.TIMEFRAME_M1)
        # print("assigning time_spectator")
        self.time_spectator = TimeSpectator.TimeSpectator(self.lower_timeframe.current_time)
        # print("assigning current_date")
        self.current_date = self.time_spectator.current_date
        # print("assigning range_spectator")
        self.range_spectator = RangeSpectator.RangeSpectator(self.time_spectator.check_time(), self.higher_timeframe.df)
        # print("assigning imbalance_spectator")
        self.imbalance_spectator = ImbalanceSpectator.ImbalanceSpectator(None)
        # print("assigning orderblock_spectator")
        self.orderblock_spectator = OrderBlockSpectator.OrderBlockSpectator(None)
        # print("assigning break_spectator")
        self.break_spectator = BreakSpectator.BreakSpectator(self.lower_timeframe.df)
        # print("updating_graph")
        self.update_graph()

    def update(self, account_balance=None, lower_df=None, higher_df=None):

        # update account balance if the trading bot is working in real-time
        if self.mode != "Simulation":
            self.account_balance = account_balance
        print(f"is simulation? {self.mode} in line 75, trading_bot.py")
        # update objects
        if lower_df is not None and higher_df is not None:
            self.lower_timeframe.update(lower_df)  # update timeframe
            self.higher_timeframe.update(higher_df)  # update timeframe
        else:
            self.lower_timeframe.update()  # update timeframe
            self.higher_timeframe.update()  # update timeframe
        self.break_spectator.update(self.lower_timeframe.df)  # update swing point
        self.time_spectator.update(self.lower_timeframe.current_time)  # update time
        can_define_range = self.time_spectator.check_time()
        self.range_spectator.update(can_define_range, self.higher_timeframe.df)  # update range

        # track pending trades
        if self.pending_trade:
            self.track_pending_trades()

        # track the trades before returning, because if the date is passed,
        # it will stop the update function directly, and reset
        if self.opened_trade:
            self.track_opened_trades()

        # update graphs
        self.update_graph()

        # check is date changed. if yes, reset all
        if self.current_date != self.time_spectator.current_date:
            self.current_date = self.time_spectator.current_date
            self.reset()
            return

        # check is the trend confirmed.
        if can_define_range and not self.range_spectator.is_trend_confirmed():
            self.range_spectator.broke_range(self.higher_timeframe.get_previous_row())

        # get the trend if trend is confirmed in the range spectator
        # self.confirmed_trend = self.range_spectator.get_trend()

        # check if the price goes opposite to the trend.
        if self.confirmed_trend == "Bullish":
            if self.higher_timeframe.get_previous_row()["close"] < self.range_spectator.range_lower_bound:
                self.reset()
                return

        elif self.confirmed_trend == "Bearish":
            if self.higher_timeframe.get_previous_row()["close"] > self.range_spectator.range_upper_bound:
                self.reset()
                return

        # if the trend is confirmed, do the following operations....
        if self.confirmed_trend:
            self.confirmed_trend_operation()

        # if the price reached equilibrium, can do the following operation
        if self.reached_equilibrium:
            self.equilibrium_operation()
        # get poi range from orderblock, as this is an order block trading robot

        # assign poi
        if self.poi:
            self.assign_poi()

        # make orders
        if self.poi_low and self.poi_high and len(self.trade) < 2:

            if self.confirmed_trend == "Bullish":
                self.proceed_order_bullish()
            elif self.confirmed_trend == "Bearish":
                self.proceed_order_bearish()
            # send order message

    def reset(self):
        self.reached_equilibrium = False
        self.confirmed_trend = ""
        self.equilibrium = 0
        self.orderblock_spectator.reset()
        self.imbalance_spectator.reset()
        self.range_spectator.reset()
        self.break_spectator.reset()
        self.poi = None

        self.poi_low = self.poi_high = 0
        self.imbalance_confirmed = False
        self.orderblock_confirmed = False
        self.bos_start_point_time = 0
        temp_array = self.trade.copy()
        # remove the trade that did not execute on the same day
        for trade in self.trade:
            if not trade.get("status"):
                temp_array.remove(trade)
        self.trade = temp_array
        self.reached_equilibrium_time = None

    def assign_poi(self):

        self.poi_low = self.poi.get("low")
        self.poi_high = self.poi.get("high")
        self.poi = None

        # maybe mark the graph here....

    def confirmed_trend_operation(self):
        # set the equilibrium
        self.equilibrium = self.range_spectator.get_equilibrium()
        # check if the price reached equilibrium
        if self.confirmed_trend == "Bullish" and self.lower_timeframe.current_low < self.equilibrium:
            self.reached_equilibrium = True

            if self.reached_equilibrium_time is None:
                self.reached_equilibrium_time = self.lower_timeframe.current_time

        elif self.confirmed_trend == "Bearish" and self.lower_timeframe.current_high > self.equilibrium:
            self.reached_equilibrium = True

            if self.reached_equilibrium_time is None:
                self.reached_equilibrium_time = self.lower_timeframe.current_time

    def equilibrium_operation(self):
        # the following operation will be done after the price reached the equilibrium
        # assign the trend to imbalance spectator
        self.imbalance_spectator.update(self.confirmed_trend)
        # assign the trend to orderblock spectator
        self.orderblock_spectator.update(self.confirmed_trend)
        # assign the trend to the break spectator
        self.break_spectator.assign_trend(self.confirmed_trend)
        # get bos range
        # check is any break of structure in that is the same as the confirmed trend
        self.bos_start_point_time = self.break_spectator.check_break_of_structure(self.reached_equilibrium_time)

        if self.bos_start_point_time is not None:
            # get imbalance from bos_range_start to end of the dataframe
            self.imbalance_spectator.find_imbalance(self.lower_timeframe.df, self.bos_start_point_time)
            self.imbalance_confirmed = self.imbalance_spectator.can_trade()

        # get orderblock
        if self.imbalance_confirmed:
            # get orderblock from the bos_range_start to the end of the dataframe

            imbalance_pois = self.imbalance_spectator.get_poi()
            imbalance_times = [elem[1] for elem in imbalance_pois]
            self.orderblock_spectator.find_ob(self.lower_timeframe.df, max(imbalance_times))

            self.poi = self.orderblock_spectator.get_range()

    def track_pending_trades(self):
        still_has_pending_trade = False
        if self.trade:
            for trade in self.trade:
                # if the trade is already opened, no need to track the pending trades
                if trade.get("status"):
                    continue
                order_type = trade.get("type")
                entry_price = trade.get("entry")

                # tracking price in the bot, not in the server
                current_low = self.lower_timeframe.current_low
                current_high = self.lower_timeframe.current_high
                if order_type == "buy" and current_low <= entry_price:
                    trade.update({"status": True})
                    self.opened_trade = True
                    # the "continue" below is to prevent the changing the still_has_pending_trade into true
                    # because the trade is already opened for this situation,
                    # therefore, if all the trade is opened, the still_has_pending_trade should not be turned to True
                    continue
                elif order_type == "sell" and current_high >= entry_price:
                    trade.update({"status": True})
                    self.opened_trade = True
                    continue
                still_has_pending_trade = True

        if not still_has_pending_trade:
            self.pending_trade = False

    def track_opened_trades(self):
        still_has_opening_trades = False
        temp_array = self.trade.copy()
        if self.trade:
            for trade in self.trade:
                # if the trade is not opened yet, skip the trade
                if not trade.get("status"):
                    continue

                # get the trade type
                order_type = trade.get("type")
                # get the two attribute that will trigger the close trade function
                target, stoploss = trade.get("target_profit"), trade.get("stop_loss")

                # tracking record in the bot, not in the metatrader server
                current_low = self.lower_timeframe.current_low
                current_high = self.lower_timeframe.current_high
                reason = ""
                can_close_trade = False
                if order_type == "buy" and (current_high > target):
                    # proceed win trade of buy
                    self.proceed_close_trade(trade, "win")
                    can_close_trade = True
                    reason = f"win already. Current_high {current_high} > target {target}"

                elif order_type == "buy" and (current_low < stoploss):
                    # proceed loss trade of buy
                    self.proceed_close_trade(trade, "lose")
                    can_close_trade = True
                    reason = f"lose already. Current_low {current_low}< stoploss{stoploss}"

                elif order_type == "sell" and (current_high > stoploss):
                    # proceed loss trade of sell
                    self.proceed_close_trade(trade, "lose")
                    can_close_trade = True
                    reason = f"lose already. Current_high {current_high} > stoploss{stoploss}"

                elif order_type == "sell" and (current_low < target):
                    # proceed win trade of sell
                    self.proceed_close_trade(trade, "win")
                    can_close_trade = True
                    reason = f"win already. Current_low {current_low}< target{target}"

                # the trade can be closed
                if can_close_trade:
                    temp_array.remove(trade)
                else:
                    # the trade is still opened
                    still_has_opening_trades = True

        # clear the self.trade
        self.trade = temp_array

        if not still_has_opening_trades:
            self.opened_trade = False

    def proceed_order_bullish(self, ratio=None):
        # simulate order will not send order, but enable the graph to be presented on the gui
        # and generate report as well
        entry_price = (self.poi_high + self.poi_low) / 2
        stop_loss_level = self.poi_low - (5 * self.point_value)
        stop_loss_point = int(round((entry_price - stop_loss_level) / self.point_value, 0))
        ratio = ratio if ratio else 5
        tp_level = entry_price + ((stop_loss_point * ratio) * self.point_value)
        symbol_name = self.higher_timeframe.symbol_name
        volume = calculator.calculate_volume(self.account_balance, symbol_name, stop_loss_point)
        trade = {"entry": entry_price, "stop_loss": stop_loss_level, "target_profit": tp_level, "status": False,
                 "type": "buy", "ratio": ratio}

        self.pending_trade = True
        self.trade.append(trade)

        self.reset_after_trade()
        # create real order if the mode is not simulation
        if self.mode != "Simulation":

            # do bullish order with time limit
            order.create_buy_order_limit(symbol_name, volume, stop_loss_level, entry_price, tp_level)

    def proceed_order_bearish(self, ratio=None):
        # simulate order will not send order, but enable the graph to be presented on the gui
        # and generate report as well
        entry_price = (self.poi_high + self.poi_low) / 2
        stop_loss_level = self.poi_high + (5 * self.point_value)
        stop_loss_point = int(round((stop_loss_level - entry_price) / self.point_value, 0))
        ratio = ratio if ratio else 5
        tp_level = entry_price - ((stop_loss_point * ratio) * self.point_value)
        symbol_name = self.higher_timeframe.symbol_name
        volume = calculator.calculate_volume(self.account_balance, symbol_name, stop_loss_point)
        trade = {"entry": entry_price, "stop_loss": stop_loss_level, "target_profit": tp_level, "status": False,
                 "type": "sell", "ratio": ratio}

        self.trade.append(trade)
        self.pending_trade = True

        self.reset_after_trade()
        # create real order if the mode is not simulation
        if self.mode != "Simulation":
            # do bearish order with time limit
            order.create_sell_order_limit(symbol_name, volume, stop_loss_level, entry_price, tp_level)

    def clear_poi(self):
        self.poi_low = 0
        self.poi_high = 0

    def reset_after_trade(self):
        self.imbalance_spectator.reset_imbalance()
        self.imbalance_confirmed = self.imbalance_spectator.has_imbalance
        self.clear_poi()

    def proceed_close_trade(self, trade, result):
        global  excel_folder
        # calculate results
        ratio = trade.get("ratio")

        # get balance after based on either simulation or real time trading
        if self.mode == "Simulation":
            if result == "win":
                balance_after = round(self.account_balance * (100 + ratio) / 100, 2)
            else:
                balance_after = round(self.account_balance * 99 / 100, 2)
        else:
            balance_after = mt5.account_info()._asdict()["balance"]

        trade_type = trade.get("type")  # get buy or sell
        entry_price = trade.get("entry")
        stop_loss = trade.get("stop_loss")
        tp = trade.get("target_profit")

        # generate reports
        column_names = ["Time", "Initial Balance", "Final Balance", "Trade Type","Symbol", "Entry Price",
                        "Stop Loss", "Target Profit", "Trade Result", "Ratio"]
        data = [self.lower_timeframe.current_time, self.initial_balance, balance_after, trade_type,
                self.higher_timeframe.symbol_name, entry_price, stop_loss, tp, result, ratio]
        df_towrite = pd.DataFrame(data).transpose()
        df_towrite.columns = column_names

        # assigning folder
        if self.mode == "Simulation" and "Simulation" not in str(excel_folder):
            excel_folder = pathlib.Path(excel_folder,"Simulation")
        elif self.mode != "Simulation" and "Real_Trading" not in str(excel_folder):
            excel_folder = pathlib.Path(excel_folder,"Real_Trading")
        if not os.path.exists(excel_folder):
            os.makedirs(excel_folder)

        # assigning file name
        if self.mode == "Simulation" and not self.file_name:
            self.file_name = f"Simulation_{len(os.listdir(excel_folder))+1}.xlsx"
        elif self.mode != "Simulation" and not self.file_name:
            file_name = self.lower_timeframe.current_time.strftime("%Y-%m")
            self.file_name = f"{file_name}.xlsx"
        excel_path = pathlib.Path(excel_folder, self.file_name)
        if os.path.exists(excel_path):
            df_read = pd.read_excel(excel_path)
            trade_num = len(df_read)
            df_towrite.insert(0, "Trade_No.", trade_num + 1)
            df_towrite = pd.concat([df_read, df_towrite])
        else:
            df_towrite.insert(0, "Trade_No.", 1)
        with pd.ExcelWriter(excel_path) as writer:
            df_towrite.to_excel(writer, index=False)

        # save image for referencing purpose
        image_folder = "image"
        if not os.path.exists(image_folder):
            os.makedirs(image_folder)
        image_name = f"{trade_type}_entry-{entry_price}_stoploss-{stop_loss}_result-{result}.jpg"
        image_path = pathlib.Path(image_folder,image_name)
        self.fig_lower.write_image(image_path)

        # update the initial balance after recording the data into excel
        self.initial_balance = balance_after
        if self.mode == "Simulation":
            self.account_balance = self.initial_balance

    def update_graph(self):
        # get dataframe for lower timeframe and higher timeframe
        # print("in trading_bot.update_graph")
        high_df = self.higher_timeframe.df
        low_df = self.lower_timeframe.df
        self.fig_higher = self.generate_graph(high_df, self.higher_timeframe.symbol_name, "M5")
        self.fig_lower = self.generate_graph(low_df, self.lower_timeframe.symbol_name, "M1")

    def generate_graph(self, df, symbol_name, timeframe):

        # generate figures
        fig = go.Figure(data=go.Candlestick(x=df['time'],
                                            open=df['open'],
                                            high=df['high'],
                                            low=df['low'],
                                            close=df['close']))

        fig.update(layout_xaxis_rangeslider_visible=False)
        fig.update_layout(yaxis={'side': 'right'},
                          title=f"{symbol_name} - {timeframe}")
        fig.update_xaxes()
        # fig.layout.xaxis.fixedrange = True
        fig.layout.yaxis.fixedrange = True
        current_price = self.lower_timeframe.current_price
        # line for current price
        t_first = df.iloc[0]["time"]
        t_last = df.iloc[-1]["time"]
        fig.add_shape(type="line", x0=t_first, x1=t_last, y0=current_price, y1=current_price,
                      line=dict(color="Black", width=1), name="Price")
        if self.equilibrium:
            fig.add_shape(type="line", x0=t_first, x1=t_last, y0=self.equilibrium, y1=self.equilibrium,
                          line=dict(color="Grey", width=1), name="Equilibrium")
        if self.range_spectator.is_range_defined():
            upper_bound = self.range_spectator.range_upper_bound
            lower_bound = self.range_spectator.range_lower_bound
            implied_upper = self.range_spectator.implied_upper_bound
            implied_lower = self.range_spectator.implied_lower_bound
            fig.add_shape(type="line", x0=t_first, x1=t_last, y0=upper_bound, y1=upper_bound,
                          line=dict(color="Purple", width=1), name="upper_bound")
            fig.add_shape(type="line", x0=t_first, x1=t_last, y0=lower_bound, y1=lower_bound,
                          line=dict(color="Purple", width=1), name="lower_bound")
            fig.add_shape(type="line", x0=t_first, x1=t_last, y0=implied_upper, y1=implied_upper,
                          line=dict(color="Purple", width=1, dash="dash"), name="implied_upper")
            fig.add_shape(type="line", x0=t_first, x1=t_last, y0=implied_lower, y1=implied_lower,
                          line=dict(color="Purple", width=1, dash="dash"), name="implied_lower")
        # add trade line for each trades
        if self.opened_trade:
            entry_prices = []
            stop_loss_prices = []
            tp_prices = []
            for trade in self.trade:
                if trade.get("status"):
                    entry_prices.append(trade.get("entry"))
                    stop_loss_prices.append(trade.get("stop_loss"))
                    tp_prices.append(trade.get("target_profit"))
            # add line for stop loss (Red line)
            for index, price in enumerate(stop_loss_prices):
                fig.add_shape(type="line", x0=t_first, x1=t_last, y0=price, y1=price,
                              line=dict(color="Red", width=1, dash="dash"), name=f"Stop_Loss")
            # add line for Target Profit (Green Line)
            for index, price in enumerate(tp_prices):
                fig.add_shape(type="line", x0=t_first, x1=t_last, y0=price, y1=price,
                              line=dict(color="Green", width=1, dash="dash"), name=f"Target_Profit")
            # add line for entry level (Blue Line)
            for index, price in enumerate(entry_prices):
                fig.add_shape(type="line", x0=t_first, x1=t_last, y0=price, y1=price,
                              line=dict(color="Blue", width=1, dash="dash"), name=f"Entry")
            # fig.update(line)

        return fig

    def turn_on_simulation(self):
        self.mode = "Simulation"

    def turn_on_real(self):
        self.mode = "Not Simulation"


if __name__ == "__main__":

    symbol = "EURUSD"

    # need an infinite loop to keep the machine working (achieved)
