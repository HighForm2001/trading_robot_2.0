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

# dropdown boxes
symbol_dropdown = html.Div(
    [html.P("Symbol:", style={"font-weight": "bold", "font-size": "16px", "color": "#333", "font-family": "Georgia, serif"}),
     html.Div(style={"width": "10px"}),
     dcc.Dropdown(id="symbol-dropdown", placeholder="Symbols",
                  style={"width": "300px","font-family": "Georgia, serif"} ), ],
    style={"padding": "10px", "display": "flex", "align-items": "center"},
)
timeframe_dropdown = html.Div(
    [html.P("Timeframe:", style={"font-weight": "bold", "font-size": "16px", "color": "#333", "font-family": "Georgia, serif"}),
     html.Div(style={"width": "10px"}),
     dcc.Dropdown(id="timeframe-dropdown",options=[{'label': timeframe, 'value': timeframe} for timeframe in TIMEFRAMES],
                  placeholder="Timeframes",
                  style={"width": "300px","font-family": "Georgia, serif"},
                  ),
     ],
    style={"padding": "10px", "display": "flex", "align-items": "center",},
)
dropdown_row = html.Div(
    [symbol_dropdown,
     timeframe_dropdown, ],
    style={"padding": "10px", "display": "flex", "justify-content": "center", "align-items": "center", "background-color": "#f0f8ff",},
)



# creates the layout of the App
layout = html.Div(
    [html.H1("Real Time Charts", style={
    "text-align": "center",
    "font-size": "32px",
    "color": "#333",
    "font-family": "Helvetica, Arial, sans-serif",
    "border-bottom": "2px solid #333",  # added
    "padding-bottom": "10px",  # added
}),
     dropdown_row,
     html.Hr(style={"border-color": "#ccc"}),
# html.Button("test", id="test-button"),
     # update every second
     dcc.Interval(id="update", interval=3000),
     html.Div(id="page-content", style={"padding-top": "20px"})
     ],
    style={
        "margin-left": "5%",
        "margin-right": "5%",
        "margin-top": "20px",
        "width": "90%",
        "max-width": "none",
        "background-color": "#f0f0f0",  # changed from white
        "box-shadow": "0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)",
        "border-radius": "4px",
        "padding": "20px",
        "display": "flex",  # added
        "align-items": "center",  # added
        "justify-content": "center",  # added
        "flex-direction": "column",  # added
        "font-family": "Helvetica, Arial, sans-serif",  # changed from Arial
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


# @callback(Output(component_id="test-button", component_property="n_clicks"),
#           Input(component_id="test-button", component_property="n_clicks"))
# def test_order(n_clicks):
#     if n_clicks is None:
#         raise PreventUpdate
#     global bots
#     for symbol_name in bots:
#         current_bot = bots.get(symbol_name)
#         current_bot.poi = {"low":current_bot.lower_timeframe.current_low, "high": current_bot.lower_timeframe.current_high}
#         current_bot.confirmed_trend = "Bullish"


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
