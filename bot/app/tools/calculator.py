import numpy as np
import MetaTrader5 as mt5


def calculate_volume(account_balance, symbol_name, points):
    to_risk = account_balance * 0.01
    # check_symbol_info(symbol)
    tick_value = get_tick_value(symbol_name)
    volume = to_risk / (points * tick_value)
    volume = round(volume, 2)
    return volume


def get_point_value(symbol):
    mt5.initialize()
    return mt5.symbol_info(symbol).point


def get_tick_value(symbol):
    mt5.initialize()
    return mt5.symbol_info(symbol).trade_tick_value


def profit_percentage(initial_balance, final_balance):
    profit = final_balance - initial_balance
    return profit / initial_balance * 100


def slopee(y1, y2, x1=None, x2=None):
    x1 = x1 if x1 else 1
    x2 = x2 if x2 else 2
    return (y2 - y1) / (x2 - x1)


def calculate_slopee(df_to_find):
    to_return = [np.nan] * len(df_to_find)
    value_current = value_previous = 0
    for x in range(1, len(df_to_find)):
        value_current = df_to_find[x]
        value_previous = df_to_find[x - 1]
        to_return[x] = slopee(y2=value_current, y1=value_previous)
    return to_return


def check_trending_slopee(df, l, lookback):
    """Detect whether the slopee of the moving average is same with trend in a certain lookback period
    trend = 1 means bullish trending
    trend = 2 means bearish trending
    trend = 3 means sideway"""
    if (l - lookback) < 0:
        return np.nan
    result = []

    for x in range(l - lookback, l + 1):
        result.append(df[x])
    result = np.array(result)
    if np.all(result > 0):
        return 1
    elif np.all(result < 0):
        return 2
    else:
        return 3


def get_point_size(symbol):
    tick_size = "0"
    df = mt5.symbol_info(symbol)
    if df:
        df = df._asdict()
    for row_name in df:
        if row_name == "trade_tick_size":
            tick_size = str(df[row_name])
        # if df["Unnamed: 0"][row_name] == "trade_tick_size":
        #     # print(df["Unnamed: 0"][row_name])
        #     trade_tick_index = row_name
        #     break
    if "e" in tick_size:
        a = int(tick_size.split("e-")[1])
    else:
        a = len(tick_size.split(".")[1])
    point = 10 ** a

    return point, a


def assign_trending_slopee(df, lookback):
    to_return = [np.nan] * len(df)
    for x in range(0, len(df)):
        to_return[x] = check_trending_slopee(df, x, lookback)
    return to_return
