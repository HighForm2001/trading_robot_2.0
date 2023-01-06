import datetime

# imports below are for testing purpose
# import pandas as pd
# import numpy as np
# import MetaTrader5 as mt5
# import plotly.graph_objects as go

# done testing
class RangeSpectator:
    can_define_range = False
    range_lower_bound = 0
    range_upper_bound = 0
    implied_upper_bound = 0
    implied_lower_bound = 0
    range_start_time = datetime.time(16, 30, 0)
    range_end_time = datetime.time(17, 30, 0)
    confirm_trend = None
    equilibrium = None

    def __init__(self, can_define_range, df):
        self.update(can_define_range,df)
        print(__name__ + " initialized")

    def update(self, can_define_range, df):
        self.can_define_range = can_define_range
        if can_define_range and not self.is_range_defined():
            self.define_range(df)
        elif not can_define_range:
            self.reset()

    def reset(self):
        self.range_lower_bound = 0
        self.range_upper_bound = 0
        self.implied_upper_bound = 0
        self.implied_lower_bound = 0
        self.confirm_trend = None
        self.equilibrium = None
        self.can_define_range = False

    def define_range(self, df):
        # daily range
        temp_array_lower = []
        temp_array_upper = []

        # implied daily range
        temp_array_open_close = []
        for index, rows in df.iterrows():
            converted = rows["time"].to_pydatetime()
            if self.in_between(converted.time()):
                temp_array_upper.append(rows["high"])
                temp_array_lower.append(rows["low"])
                temp_array_open_close.append(rows["open"])
                temp_array_open_close.append(rows["close"])
        if temp_array_open_close:
            self.implied_lower_bound = min(temp_array_open_close)
            self.implied_upper_bound = max(temp_array_open_close)
        if temp_array_upper:
            self.range_upper_bound = max(temp_array_upper)
        if temp_array_lower:
            self.range_lower_bound = min(temp_array_lower)

    def in_between(self, time):
        return self.range_start_time <= time <= self.range_end_time

    def broke_range(self, previous_row):
        if not self.is_range_defined():
            return
        price = previous_row["close"]
        check_time = previous_row["time"].to_pydatetime().time()
        if self.confirm_trend or check_time < datetime.time(17, 35, 0):
            return
        if price > self.implied_upper_bound:
            self.confirm_trend = "Bullish"
            self.calculate_equilibrium()
        elif price < self.implied_lower_bound:
            self.confirm_trend = "Bearish"
            self.calculate_equilibrium()

    def calculate_equilibrium(self):
        if not self.equilibrium:
            self.equilibrium = (self.range_lower_bound + self.range_upper_bound) / 2

    def get_equilibrium(self):
        if not self.equilibrium:
            return False
        return self.equilibrium

    def is_trend_confirmed(self):
        return bool(self.confirm_trend)

    def get_trend(self):
        return self.confirm_trend

    def is_range_defined(self):
        return (self.range_upper_bound > 0 and self.implied_upper_bound > 0 and
               self.range_lower_bound > 0 and self.implied_lower_bound > 0)


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
#     test_df = pd.DataFrame(mt5.copy_rates_from_pos("US30", mt5.TIMEFRAME_M15, 10, 100))
#     test_df["time"] = pd.to_datetime(test_df["time"], unit="s")
#     test_df["signal"] = [np.nan] * len(test_df)
#     test = RangeSpectator(True,test_df)
#
#     test_df['pointpos'] = test_df.apply(lambda row: pointpos(row), axis=1)
#     fig = go.Figure(data=go.Candlestick(x=test_df["time"],
#                                         open=test_df["open"],
#                                         close=test_df["close"],
#                                         high=test_df["high"],
#                                         low=test_df["low"]))
#     test.broke_range(33096.68,datetime.time(17,40,0))
#     # fig.add_scatter(x=test_df["time"], y=test_df["pointpos"],
#     #                 mode="markers",
#     #                 marker=dict(color="MediumPurple", size=5),
#     #                 name="signal")
#     fig.add_shape(x0=test_df.iloc[0]["time"], x1= test_df.iloc[-1]["time"],
#                   y0= test.range_upper_bound, y1 = test.range_upper_bound,
#                   line=dict(color="red",dash="dash"),
#                   name="upper")
#     fig.add_shape(x0=test_df.iloc[0]["time"], x1=test_df.iloc[-1]["time"],
#                   y0=test.range_lower_bound, y1=test.range_lower_bound,
#                   line=dict(color="red", dash="dash"),
#                   name="lower")
#     fig.add_shape(x0=test_df.iloc[0]["time"], x1=test_df.iloc[-1]["time"],
#                   y0=test.implied_upper_bound, y1=test.implied_upper_bound,
#                   line=dict(color="purple", dash="dash"),
#                   name="upper")
#     fig.add_shape(x0=test_df.iloc[0]["time"], x1=test_df.iloc[-1]["time"],
#                   y0=test.implied_lower_bound, y1=test.implied_lower_bound,
#                   line=dict(color="purple", dash="dash"),
#                   name="lower")
#     fig.add_shape(x0=test_df.iloc[0]["time"], x1=test_df.iloc[-1]["time"],
#                   y0=test.equilibrium, y1=test.equilibrium,
#                   line=dict(color="green", dash="dot"),
#                   name="equilibrium")
#     test.broke_range(33096.68, datetime.time(17, 20, 0))
#     fig.show()
