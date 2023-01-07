import MetaTrader5 as mt5
import pandas as pd


class ChartSpectator:
    symbol_name = None
    time_frame = None
    df = None  # dataframe of the file
    current_time = None
    current_price = None
    current_low = None
    current_high = None

    def __init__(self, symbol, time_frame, df=None):
        # previous_30_day = (datetime.datetime.today() - datetime.timedelta(days=30)).replace(hour=0, minute=0, second=0,
        #                                                                                     microsecond=0)
        # self.df = pd.DataFrame(mt5.copy_rates_range(symbol, time_frame, previous_30_day, datetime.datetime.now()))
        # if len(df) > 0:
        if df is not None:
            self.df = df
        else:
            self.df = pd.DataFrame(mt5.copy_rates_from_pos(symbol, time_frame, 0, 30))
            self.df["time"] = pd.to_datetime(self.df["time"], unit="s")
            print(self.df)

        self.symbol_name = symbol
        self.time_frame = time_frame
        # self.current_time = self.df["time"][len(self.df) - 1]
        # self.current_price = self.df["close"][len(self.df) - 1]
        # self.current_low = self.df["low"][len(self.df) - 1]
        # self.current_high = self.df["high"][len(self.df) - 1]
        # print(f"self.df in ChartSpectator: {self.df}\ntimeframe is {time_frame}")

        self.current_time = self.df.iloc[-1]["time"].to_pydatetime()
        self.current_price = self.df.iloc[-1]["close"]
        self.current_low = self.df.iloc[-1]["low"]
        self.current_high = self.df.iloc[-1]["high"]
        print(__name__ + " initialized")
        # can_trade = self.check_time(self.current_time)

    def update(self, updated_dataframe=None):
        # real time mode
        if updated_dataframe is None:
            updated_dataframe = pd.DataFrame(mt5.copy_rates_from_pos(self.symbol_name, self.time_frame, 0, 1))
            self.current_time = self.df.iloc[-1]["time"].to_pydatetime()
            self.current_price = updated_dataframe["close"][0]
            self.current_low = updated_dataframe["low"][0]
            self.current_high = updated_dataframe["high"][0]
            # print("===========================\nUpdated_dataframe is None\n===================")
        # simulation mode
        else:
            self.current_time =  updated_dataframe["time"].to_pydatetime()
            self.current_price = updated_dataframe["close"]  # [0]
            self.current_low = updated_dataframe["low"]
            self.current_high = updated_dataframe["high"]
        updated_dataframe["time"] = pd.to_datetime(updated_dataframe["time"],unit="s")
        self.df = self.df.append(updated_dataframe)
        self.df.drop_duplicates(['time'], keep="last", inplace=True)

        if len(self.df) > 60:
            self.df = self.df.tail(60)
        self.df.index = range(len(self.df))
            # print(f"self.df in ChartSpectator if len(self.df) > 30\ntimeframe:{self.time_frame}\n{self.df}")
        # print(f"updated_dataframe(in chart spectator):{updated_dataframe}")
        # print(f"df{self.df}")


    def get_previous_row(self):
        return self.df.iloc[-2]
    # def get_trend(self):
    #     if "MA9" not in self.df.columns:
    #         self.df["EMA9"] = ta.ema(self.df["close"], 9)
    #     if "MA18" not in self.df.columns:
    #         self.df["EMA18"] = ta.ema(self.df["close"], 18)
    #     last_row = self.df.iloc[-1:]
    #     if last_row["EMA9"] > last_row["EMA18"]:
    #         return "Bullish"
    #     return "Bearish"
