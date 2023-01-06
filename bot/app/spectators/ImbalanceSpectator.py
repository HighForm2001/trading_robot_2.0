from tools import pattern


# imports below are for testing purpose
# import pattern
# import MetaTrader5 as mt5
# import pandas as pd
# import numpy as np
# import plotly.graph_objects as go


class ImbalanceSpectator:
    direction = None
    has_imbalance = False
    # data structure of imbalances:
    # [imbalance1, imbalance2, imbalance3, etc....]
    # [[area_low,area_high], [area_low, area_high]]
    imbalances = []

    def __init__(self, direction):

        self.update(direction)
        print(__name__ + " initialized")

    def find_imbalance(self, given_df, bos_start_time):
        first_candle = second_candle = third_candle = None
        for index, row in given_df.iterrows():
            # if the data is before the bos happened, skip
            # only proceed the data where the time is after the bos happened
            # continue here. next thing to change: check ob_time.
            if row["time"].to_pydatetime() < bos_start_time:
                continue
            if type(first_candle) == type(None):
                first_candle = row
                continue

            if type(second_candle) == type(None):
                second_candle = row
                continue

            if type(third_candle) == type(None):
                third_candle = row
                self.__operation(first_candle, second_candle, third_candle)
                continue

            first_candle = second_candle
            second_candle = third_candle
            third_candle = row
            self.__operation(first_candle, second_candle, third_candle)

    def update(self, direction):
        self.direction = direction

    def __operation(self, first_candle, second_candle, third_candle):
        # data structure of imbalance:
        # [area_low, area_high]
        result, imbalance = pattern.imbalance(first_candle, second_candle, third_candle, self.direction)

        if result:
            # self.imbalances[0] = [area_low, area_high], if + time,
            # self.imbalances[0] = ([area_low, area_high], time)
            self.imbalances.append((imbalance, first_candle["time"].to_pydatetime()))
            if not self.has_imbalance:
                self.has_imbalance = result

    def can_trade(self):
        return self.has_imbalance

    def get_poi(self):
        return self.imbalances

    def reset(self):
        self.reset_imbalance()
        self.direction = None
        self.imbalances = []

    def reset_imbalance(self):
        self.has_imbalance = False
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
#     test = ImbalanceSpectator("Bearish")
#     test.find_imbalance(test_df)
#     for imbalance in test.imbalances:
#         test_df.at[imbalance[1], "signal"] = 1
#     test.update("Bullish")
#     test.find_imbalance(test_df)
#     for imbalance in test.imbalances:
#         test_df.at[imbalance[1], "signal"] = 1
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
