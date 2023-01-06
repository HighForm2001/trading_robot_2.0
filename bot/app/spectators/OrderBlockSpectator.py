from tools import pattern

# imports below are for testing purpose
# import pattern
# import numpy as np
# import MetaTrader5 as mt5
# import pandas as pd
# import plotly.graph_objects as go

class OrderBlockSpectator:
    current_trend = None
    ob_range = {}
    lowest_candle_position = highest_candle_position = 0
    returned_ob_range = []

    def __init__(self, ob_type):
        self.update(ob_type)
        print(__name__ + " initialized")

    def update(self, ob_type):
        self.current_trend = ob_type

    def find_ob(self, given_df,imbalance_time): # imbalance_time is already transformed to pydatetime
        given_df = given_df.iloc[::-1]
        found_first = False  # find at least one opposite direction candle of the trend direction
        for index, row in given_df.iterrows():
            row_time = row["time"].to_pydatetime()
            if row_time > imbalance_time:
                continue
            candle_pattern = pattern.check_candle_type(row["open"], row["close"])
            if self.current_trend == "Bullish":
                if candle_pattern == 0:
                    if self.ob_range:
                        self.ob_range.update({"high": row["high"]})
                        self.highest_candle_position = index
                    else:
                        self.ob_range.update({"low": row["low"], "high": row["high"]})
                        self.lowest_candle_position = index
                    found_first = True
                else:
                    if not found_first:
                        continue
                    break
            else:  # Bearish OB
                if candle_pattern == 1:
                    if self.ob_range:
                        self.ob_range.update({"low": row["low"]})
                        self.lowest_candle_position = index
                    else:
                        self.ob_range.update({"low": row["low"], "high": row["high"]})
                        self.highest_candle_position = index
                    found_first = True
                else:
                    if not found_first:
                        continue
                    break


    def reset(self):
        self.ob_range.clear()
        self.returned_ob_range.clear()

    def get_range(self):
        if self.ob_range not in self.returned_ob_range:
            self.returned_ob_range.append(self.ob_range)
            return self.ob_range
        return None

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
#     test = OrderBlockSpectator("Bearish")
#     test.find_ob(test_df)
#     test_df.at[test.lowest_candle_position,"signal"] = 2
#     test_df.at[test.highest_candle_position,"signal"] = 1
#     print(f"Bearish OB: {test.lowest_candle_position},{test.highest_candle_position}")
#     test.update("Bullish")
#
#     test.find_ob(test_df)
#     test_df.at[test.lowest_candle_position, "signal"] = 2
#     test_df.at[test.highest_candle_position, "signal"] = 1
#     print(f"Bullish OB: {test.lowest_candle_position},{test.highest_candle_position}")
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
