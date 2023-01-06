import dash
from dash import Dash, html, dcc, Input, Output, State, callback
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import MetaTrader5 as mt5
from pages.mt5_funcs import get_symbol_names, TIMEFRAMES, TIMEFRAME_DICT, get_account_info

import trading_bot

dash.register_page(__name__)
# creates the Dash App
# app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
obtained_pair = []
bots = {}
length = 0
symbol_dropdown = html.Div(
    [html.P("Symbol:", style={"font-weight": "bold"}),
     dcc.Dropdown(id="symbol-dropdown", placeholder="Please select the pair to look for charts.",
                  style={"width": "200px", "font-size": "16px"}, ), ],
    style={"padding": "10px"},
)

timeframe_dropdown = html.Div(
    [html.P("Timeframe:", style={"font-weight": "bold"}), dcc.Dropdown(id="timeframe-dropdown",
                                                                       options=[{'label': timeframe, 'value': timeframe}
                                                                                for timeframe in TIMEFRAMES],
                                                                       placeholder="Please select the timeframe to look for charts.",
                                                                       style={"width": "200px", "font-size": "16px"},
                                                                       ),
     ],
    style={"padding": "10px"},
)

# creates the layout of the App
layout = html.Div(
    [html.H1("Real Time Charts", style={"text-align": "center", "font-size": "32px"}),
     dbc.Row(
         [dbc.Col(symbol_dropdown, style={"padding-right": "20px"}),
          dbc.Col(timeframe_dropdown, style={"padding-right": "20px"}), ]
     ),
     html.Hr(),
     # update every second
     dcc.Interval(id="update", interval=3000),
     html.Div(id="page-content"),
     html.Button("test", id="test-button")
     ],
    style={
        "margin-left": "5%",
        "margin-right": "5%",
        "margin-top": "20px",
        "width": "90%",
        "max-width": "none",
    },
)


@callback(
    Output('page-content', 'children'),
    Input('update', 'n_intervals'),
    State('symbol-dropdown', 'value'), State('timeframe-dropdown', 'value')
)
def update_ohlc_chart(interval, symbol, timeframe):
    if not symbol or not timeframe:
        raise PreventUpdate
    global bots
    # timeframe = TIMEFRAME_DICT[timeframe]
    # update_dataset()
    update_bots()
    selected_bot = bots.get(symbol)
    if timeframe == "M1":
        fig = selected_bot.fig_lower
    else:
        fig = selected_bot.fig_higher
    return [dcc.Graph(figure=fig, config={'displayModeBar': False})]


@callback(
    Output('symbol-dropdown', 'options'),
    Input('update', 'n_intervals'),
    State('symbol-dropdown', 'options')
)
def update_symbol_dropdown(n_intervals, options):
    print(f"options:{options}")
    global obtained_pair, bots
    value = ""
    with open("pages/pair/pair.txt", "r") as read:
        value = read.readline()
    value = value.split("|")
    new_pair = set(value).difference(obtained_pair)
    for pair in new_pair:
        if pair != "":
            # initialize_dataset(pair)
            initialize_bot(pair)
            obtained_pair.append(pair)
    # generate df.

    return value


@callback(Output(component_id="test-button", component_property="n_clicks"),
          Input(component_id="test-button", component_property="n_clicks"))
def test_order(n_clicks):
    if n_clicks is None:
        raise PreventUpdate
    global bots
    for symbol_name in bots:
        current_bot = bots.get(symbol_name)
        current_bot.poi = {"low":current_bot.lower_timeframe.current_low, "high": current_bot.lower_timeframe.current_high}
        current_bot.confirmed_trend = "Bullish"


def initialize_bot(pair):
    global bots
    account_balance = get_account_info().get("balance")
    trading_ai = trading_bot.Bot(pair, account_balance)
    trading_ai.turn_on_real()
    bots.update({pair: trading_ai})



def update_bots():
    global bots
    print(bots)
    for symbol_name in bots:
        bots.get(symbol_name).update(account_balance=get_account_info().get("balance"))




def get_candlestick_chart(pair, timeframe):
    global bots
    return bots[(pair, timeframe)]
