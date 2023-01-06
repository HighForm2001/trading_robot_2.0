import MetaTrader5 as mt5


def create_buy_order_now(symbol, volume, stop_loss):
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": mt5.ORDER_TYPE_BUY,
        "price": mt5.symbol_info_tick(symbol).ask,
        "sl": stop_loss,
        "tp": 0.0,
        "deviation": 200,
        "magic": 13345920,
        "commmit": "python script order: create_buy_order_now()",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC
    }
    order_request = mt5.order_send(request)
    print(order_request)
    # return request


def create_sell_order_now(symbol, volume, stop_loss):
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": mt5.ORDER_TYPE_SELL,
        "price": mt5.symbol_info_tick(symbol).bid,
        "sl": stop_loss,
        "tp": 0.0,
        "deviation": 200,
        "magic": 13345920,
        "commmit": "python script order: create_sell_order_now()",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC
    }
    order_request = mt5.order_send(request)
    print(order_request)


def create_sell_order_limit(symbol, volume, stop_loss, price,tp_level = None):
    request = {
        "action": mt5.TRADE_ACTION_PENDING,
        "symbol": symbol,
        "volume": volume,
        "type": mt5.ORDER_TYPE_SELL_LIMIT,
        "price": price,
        "sl": stop_loss,
        "tp": tp_level if tp_level else 0.0,
        "deviation": 200,
        "magic": 13345920,
        "commmit": "python script order: create_sell_order_limit()",
        "type_time": mt5.ORDER_TIME_DAY,
        "type_filling": mt5.ORDER_FILLING_IOC
    }
    order_request = mt5.order_send(request)
    print(order_request)


def create_buy_order_limit(symbol, volume, stop_loss, price, tp_level = None):
    request = {
        "action": mt5.TRADE_ACTION_PENDING,
        "symbol": symbol,
        "volume": volume,
        "type": mt5.ORDER_TYPE_BUY_LIMIT,
        "price": price,
        "sl": stop_loss,
        "tp": tp_level if tp_level else 0.0,
        "deviation": 200,
        "magic": 13345920,
        "commmit": "python script order: create_buy_order_limit()",
        "type_time": mt5.ORDER_TIME_DAY,
        "type_filling": mt5.ORDER_FILLING_IOC
    }
    order_request = mt5.order_send(request)
    print(order_request)
    #
