import datetime

# imports below are for testing purpose
# import MetaTrader5 as mt5
# import pandas as pd
# import numpy as np
# import plotly.graph_objects as go


# done testing
class TimeSpectator:
    # asian_start = datetime.time(2, 0, 0)
    # asian_end = datetime.time(4, 0, 0)
    # london_open_start = datetime.time(9, 0, 0)
    # london_open_end = datetime.time(12, 0, 0)
    # new_york_open_start = datetime.time(14, 0, 0)
    # new_york_open_end = datetime.time(17, 0, 0)
    current_time = None
    current_date = None
    working_time_start = datetime.time(17, 35, 0)

    def __init__(self, time):
        self.update(time)
        print(__name__ + " initialized")
        # self.current_date = time.to_pydatetime().date()

    def check_time(self):
        return self.current_time >= self.working_time_start

    def update(self, given_time):
        self.current_time = given_time.time()
        self.current_date = given_time.date()

    # def get_previous_session(self):
    #     if self.asian_end < self.current_time < self.london_open_start:
    #         return "Asian"
    #     elif self.london_open_end < self.current_time < self.new_york_open_start:
    #         return "London"
    #     elif self.new_york_open_end < self.current_time < self.asian_end:
    #         return "New York"


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
#     test = TimeSpectator(test_df["time"][0])
#     test_df.at[0, "signal"] = 1 if test.check_time() else 0
#     for i in range(1, len(test_df)):
#         test.update(test_df["time"][i])
#         if test.check_time():
#             current_time = test_df["time"][i]
#             print(f"is in working time! {current_time}")
#             test_df.at[i, "signal"] = 1
#             signals = test_df["signal"][i]
#             print(f"assigned value: {signals}")
#     test_df['pointpos'] = test_df.apply(lambda row: pointpos(row), axis=1)
#     fig = go.Figure(data=go.Candlestick(x=test_df["time"],
#                                         open=test_df["open"],
#                                         close=test_df["close"],
#                                         high=test_df["high"],
#                                         low=test_df["low"]))
#     fig.add_scatter(x=test_df["time"], y=test_df["pointpos"],
#                     mode="markers",
#                     marker=dict(color="MediumPurple", size=5),
#                     name="signal")
#     fig.show()
