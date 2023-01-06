import MetaTrader5 as mt5
import pandas as pd
import re

TIMEFRAMES = ['M1', 'M5']#, 'M15', 'M30', 'H1', 'H4', 'D1', 'W1', 'MN1']
TIMEFRAME_DICT = {
    'M1': mt5.TIMEFRAME_M1,
    'M5': mt5.TIMEFRAME_M5
    # 'M15': mt5.TIMEFRAME_M15,
    # 'M30': mt5.TIMEFRAME_M30,
    # 'H1': mt5.TIMEFRAME_H1,
    # 'H4': mt5.TIMEFRAME_H4,
    # 'D1': mt5.TIMEFRAME_D1,
    # 'W1': mt5.TIMEFRAME_W1,
    # 'MN1': mt5.TIMEFRAME_MN1,
}


def get_symbol_names():
    # connect to MetaTrader5 platform
    mt5.initialize()

    # get symbols
    symbols = mt5.symbols_get()
    symbols_df = pd.DataFrame(symbols, columns=symbols[0]._asdict().keys())
    symbol_names = symbols_df['name'].tolist()
    # filtered_symbol_names = [elem for elem in symbol_names if any(char.isdigit() for char in elem)]
    return symbol_names


def get_account_info():
    mt5.initialize()
    account = mt5.account_info()
    account_df = account._asdict()
    extracted = {"account_number": account_df['login'], "leverage": account_df["leverage"],
                 "balance": account_df["balance"], "profit": account_df["profit"],
                 "equity": account_df["equity"], "account_name": account_df["name"],
                 "server": account_df["server"], "currency": account_df["currency"], "broker": account_df["company"]}

    # print(account_df)
    # print(account_df["login"])
    return extracted
    # return account_df


if __name__ == "__main__":

    print(get_account_info().get("balance"))
    # get_symbol_names()
