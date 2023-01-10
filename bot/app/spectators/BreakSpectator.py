from tools import pattern


# imports below are for testing purpose
# import pattern
# import MetaTrader5 as mt5
# import pandas as pd
# import numpy as np
# import plotly.graph_objects as go
class BreakSpectator:
    swing_highs = []
    swing_lows = []
    nearest_swing_high = None
    nearest_swing_low = None
    swing_low_position = None
    swing_high_position = None
    current_trend = None
    can_open_trade = False
    # self.bos_element structure
    # (break structure price, invalid price)
    bos_element = ()
    invalided_prices = []


    def __init__(self, df):
        self.update(df)
        print(__name__ + " initialized")

    def __operation(self, df_given):
        # clear the swing_lows and swing_highs so it can always find the
        # latest three highs and lows
        self.swing_lows.clear()
        self.swing_highs.clear()
        df_given.index = range(len(df_given))
        df = df_given.iloc[::-1].copy()
        for index, row in df.iterrows():
            if index < 2 or index > len(df) - 3:
            # if index < 1 or index > len(df) - 2:
                continue
            # if len(self.swing_highs) >= 3 and len(self.swing_lows) >= 3:
            if len(self.swing_highs) >= 2 and len(self.swing_lows) >= 2:
                break
            if self.nearest_swing_high and self.nearest_swing_low:
                break
            next2_candle_high = df.at[index+2, "high"]
            next2_candle_low = df.at[index+2,"low"]
            next_candle_high = df.at[index + 1, "high"]
            next_candle_low = df.at[index + 1, "low"]
            previous_candle_high = df.at[index - 1, "high"]
            previous_candle_low = df.at[index - 1, "low"]
            previous2_candle_high = df.at[index - 2, "high"]
            previous2_candle_low = df.at[index - 2, "low"]
            current_candle_high = row["high"]
            current_candle_low = row["low"]
            # if pattern.pivot_point(previous_candle_low, current_candle_low, next_candle_low,
            #                        1) and len(self.swing_lows) < 3:
            if pattern.pivot_point(previous_candle_low, current_candle_low, next_candle_low,
                                   1,previous_2 = previous2_candle_low, next_2 = next2_candle_low) and len(self.swing_lows) < 2:
                self.swing_lows.append((current_candle_low, index, row["time"].to_pydatetime()))
            # if pattern.pivot_point(previous_candle_low, current_candle_low, next_candle_low,
            #                        1) and self.nearest_swing_low is None:
            #     self.nearest_swing_low = current_candle_low
            #      self.swing_low_position = i
            # if pattern.pivot_point(previous_candle_high, current_candle_high, next_candle_high,
            #                        2) and len(self.swing_highs) < 3:
            if pattern.pivot_point(previous_candle_high, current_candle_high, next_candle_high,
                                   2,previous_2 = previous2_candle_high, next_2 =next2_candle_high) and len(self.swing_highs) < 2:
                self.swing_highs.append((current_candle_high, index, row["time"].to_pydatetime()))


    def update(self, df):
        self.__operation(df)
        current_price_row = df.iloc[-1]
        if self.current_trend == "Bearish":
            check_price = current_price_row["high"]
            # self.bos_element structure
            # (break structure price, invalid price)
            if self.can_open_trade and check_price > self.bos_element[1]:
                self.invalided_prices.append(self.bos_element[0])
                self.update_reset()
        elif self.current_trend == "Bullish":
            check_price = current_price_row["low"]
            if self.can_open_trade and check_price < self.bos_element[1]:
                self.invalided_prices.append(self.bos_element[0])
                self.update_reset()

    def check_break_of_structure(self, reached_equilibrium_time):

        if self.current_trend and self.current_trend == "Bullish":
            if len(self.swing_highs) < 2:
                return None
            current_high_time = self.swing_highs[0][2]
            if current_high_time <= reached_equilibrium_time:
                return None

            current_high = self.swing_highs[0]
            previous_high = self.swing_highs[1]
            # second_previous_high = self.swing_highs[2]
            if current_high[0] in self.invalided_prices:
                return None
            # if the high is getting lower, but the current high is higher than the previous,
            # then consider it is a break of structure.
            # it is a tuple. the first element stores the price
            # the second element stores the position
            # if previous_high[0] < second_previous_high[0] and current_high[0] > previous_high[0]:
            if current_high[0] > previous_high[0]:
                self.can_open_trade = True
                # self.bos_element structure
                # (break structure price, invalid price)
                self.bos_element = (current_high[0],self.swing_lows[0][0])

                # return position to the caller
                return self.swing_lows[0][2]

        elif self.current_trend and self.current_trend == "Bearish":
            if len(self.swing_lows) < 2:
                return None
            current_low_time = self.swing_lows[0][2]
            if current_low_time <= reached_equilibrium_time:
                return None

            current_low = self.swing_lows[0]
            previous_low = self.swing_lows[1]

            if current_low[0] in self.invalided_prices:
                return None

            # if the low is getting higher, but the current low is lower than the previous,
            # then consider it is a break of structure
            # it is a tuple. the first element stores the price
            # the second element stores the position
            # if previous_low[0] > second_previous_low[0] and current_low[0] < previous_low[0]:
            if current_low[0] < previous_low[0]:
                self.can_open_trade = True
                # (break structure price, invalid price)
                self.bos_element = (current_low[0], self.swing_highs[0][0])
                return self.swing_highs[0][2]

        return None

    def assign_trend(self, current_trend):
        self.current_trend = current_trend

    def reset(self):
        self.invalided_prices = []
        self.update_reset()

    def update_reset(self):
        self.bos_element = ()
        self.can_open_trade = False


# def pointpos(x):
#     if x['signal'] == 1:
#         return x['high'] + 1e-3
#     elif x['signal'] == 2:
#         return x['low'] - 1e-3
#     else:
#         return np.nan
#
#
# if __name__ == "__main__":
#     mt5.initialize()
#     test_df = pd.DataFrame(mt5.copy_rates_from_pos("US30", mt5.TIMEFRAME_M15, 0, 100))
#     test_df["time"] = pd.to_datetime(test_df["time"], unit="s")
#     test_df["signal"] = [np.nan] * len(test_df)
#     test = BreakSpectator(test_df)
#     swing_highs = test.swing_highs
#     swing_lows = test.swing_lows
#     for high in swing_highs:
#         test_df.at[high[1],"signal"] = high[0]
#     for low in swing_lows:
#         test_df.at[low[1],"signal"] = low[0]
#     # test_df['pointpos'] = test_df.apply(lambda row: pointpos(row), axis=1)
#     fig = go.Figure(data=go.Candlestick(x=test_df["time"],
#                                         open=test_df["open"],
#                                         close=test_df["close"],
#                                         high=test_df["high"],
#                                         low=test_df["low"]))
#     fig.add_scatter(x=test_df["time"], y=test_df["signal"],
#                     mode="markers",
#                     marker=dict(color="MediumPurple", size=5),
#                     name="signal")
#     fig.show()

# import pattern
#
#
# class BreakSpectator:
#     first_break = False
#     second_break = False
#     can_open_trade = False
#     nearest_swing_high = None
#     nearest_swing_low = None
#     first_break_direction = "Undefined"
#     second_break_direction = "Undefined"
#     trade_direction = "Undefined"
#
#     def __init__(self, df):
#         self.__operation(df)
#
#     def check_market_shift(self, price):
#         """To open a trade, the market shift direction need to be either up,down,up, or down,up,down."""
#         # situation
#         # break up, break down, break up, enter bullish
#         # break up, break up, invalid
#         # break up, break down, break down, nothing
#         # break down, break up, break down, enter bearish
#         # break down, break down, invalid
#         # break down, break up, break up, nothing
#         if self.can_open_trade:
#             return
#         if price > self.nearest_swing_high:
#             if not self.first_break and self.first_break_direction == "Undefined":
#                 # first time break
#                 self.first_break = True
#                 self.first_break_direction = "up" # set the break direction to up
#             elif self.first_break and self.first_break_direction == "up" and not self.second_break:
#                 # second time break
#                 # but break to the same direction
#                 pass # do nothing for this one
#             elif self.first_break and self.first_break_direction == "down" and not self.second_break:
#                 # second time break, but break to the opposite direction
#                 self.second_break = True
#                 self.second_break_direction = "up"
#             elif self.first_break and self.second_break and self.first_break_direction == "up" and self.second_break_direction == "down":
#                 self.can_open_trade = True
#                 self.trade_direction = "up"
#         elif price < self.nearest_swing_low:
#             if not self.first_break and self.first_break_direction == "Undefined":
#                 # first time break
#                 self.first_break = True
#                 self.first_break_direction = "down"
#             elif self.first_break and self.first_break_direction == "down" and not self.second_break:
#                 # second time break
#                 # but break to the same direction
#                 pass
#             elif self.first_break and self.first_break_direction == "up" and not self.second_break:
#                 # second time break
#                 # but break to the opposite direction
#                 self.second_break = True
#                 self.second_break_direction = "down"
#             elif self.first_break and self.second_break and self.first_break_direction == "down" and self.second_break_direction == "up":
#                 self.can_open_trade = True
#                 self.trade_direction = "down"
#
#
#
#     def trade_reset(self):
#         self.can_open_trade = False
#         self.first_break_direction = "Undefined"
#         self.second_break_direction = "Undefined"
#         self.first_break = False
#         self.second_break = False
#
