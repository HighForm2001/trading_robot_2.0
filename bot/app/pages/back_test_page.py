from datetime import datetime
from datetime import timedelta

import MetaTrader5 as mt5
import dash
import pandas as pd
# from bot.app.bot import Bot
import trading_bot
from dash import html, dcc, Input, Output, State, callback
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
# from bot.app.pages.mt5_funcs import get_symbol_names
from pages.mt5_funcs import get_symbol_names

# register the page to the app
dash.register_page(__name__)

# symbol dropdown component
trading_pairs = []
while not trading_pairs:
    trading_pairs = get_symbol_names()
    trading_pairs.sort()
symbol_dropdown = html.Div([
    dcc.Dropdown(id='symbol-dropdown', options=[{'label': symbol, 'value': symbol} for symbol in trading_pairs],
                 placeholder="Please select pairs to trade." if get_symbol_names() else "You are not connected to "
                                                                                        "MetaTrader5",
                 style={"width": "300px"}
                 )
], style={"display": "flex", "align-items": "center"})

# symbol_dropdown = html.Div([
#     html.P('Symbol:'),
#     dcc.Dropdown(
#         id='symbol-dropdown',
#         options=[{'label': symbol, 'value': symbol} for symbol in trading_pairs],
#         # options = [],
#         placeholder="Please select pairs to trade." if get_symbol_names() else "You are not connected to MetaTrader5"
#     )
# ])

# input area
account_balance = dcc.Input(id="balance-input", type="number",
                            value=100,
                            step=1,
                            placeholder="Account balance:",
                            min=100,
                            style={"width": "100px"}
                            )
skip_box = dcc.Input(id="skip-time", type="number",
                     step=1,
                     placeholder="Time to skip (in minutes)",
                     min=1,
                     style={"width": "200px"}
                     )

# figures
fig_lower = None
fig_higher = None

# bot
simulation_bot: trading_bot.Bot = None  # trading_bot.Bot(trading_pairs[0], account_balance, lower_df=None,
# higher_df=None)

# get today's date
today_date = datetime.now().date().strftime("%Y-%m-%d")
minimal_date = datetime.now() - timedelta(days=365 * 3)
minimal_date = datetime.replace(minimal_date, month=1, day=1).strftime("%Y-%m-%d")

# global variable
previous_start_date = previous_end_date = previous_symbol = ""
previous_balance = 0

# current timeframe
current_timeframe = "M5"

# mode
current_mode = "Manual"

# dataframes for backtest
lower_df = pd.DataFrame()
higher_df = pd.DataFrame()

# date picker
date_picker = dcc.DatePickerRange(id="date-range",
                                  start_date=None,
                                  end_date=None,
                                  min_date_allowed=minimal_date,
                                  max_date_allowed=today_date,
                                  minimum_nights=3,
                                  disabled=False,
                                  style={"border": "1px solid #ced4da", "border-radius": "5px"})

# buttons
button_style = {
    "background-color": "lightgreen",
    "color": "white",
    "padding": "10px 20px",
    "border": "none",
    "font-size": "16px",
    "border-radius": "5px",
    "cursor": "pointer",
    "outline": "none",
    "box-shadow": "0 2px 4px rgba(0, 0, 0, 0.2)",
    "font-family": "Georgia, serif"
}

start_button = html.Button("Start Backtesting!", id="start-button",
                           disabled=True, style=button_style)

m5_button = html.Button("M5", id="m5-button",
                        disabled=True, style=button_style)
m1_button = html.Button("M1", id="m1-button",
                        disabled=True, style=button_style)

next_button = html.Button("Next Candle", id="next-button",
                          disabled=True, style=button_style)

auto_button = html.Button("Auto Mode", id="auto-button",
                          style=button_style)

manual_button = html.Button("Manual Mode", id="manual-button",
                            style=button_style, disabled=True)

skip_button = html.Button("Skip now!", id="skip-button",
                          style=button_style)
skip_all_button = html.Button("Skip All", id="skip-all",
                              style=button_style)
# counter
counter = dcc.Interval(id="counter")

# graph
m5_graph = dcc.Graph(id="m5-graph", figure={"data": [], "layout": {}}, style={"display": "none"})
m1_graph = dcc.Graph(id="m1-graph", figure={"data": [], "layout": {}}, style={"display": "none"})

# rows
table_style = {"border": "none", "border-collapse": "collapse", "padding": "10px", "border-spacing": "5px",
               "font-family": "Georgia, serif"}
td_style = {"border": "none", "text-align": "center", "padding": "10px"}

input_table = html.Table([html.Tr(
    [html.Td([html.P("Select the date range: ")], style=td_style),
     html.Td([date_picker], style=td_style)
     ]),
    html.Tr([html.Td([html.P("Select the symbol:")], style=td_style),
             html.Td([symbol_dropdown], style=td_style)
             ]),
    html.Tr([html.Td([html.P("Enter simulation balance: ")], style=td_style),
             html.Td([account_balance], style=td_style)
             ]),
    html.Tr([html.Td([start_button], colSpan=2, style=td_style)
             ]),
], style=table_style)
table_div = html.Div([input_table],
                     style={"padding": "10px", "display": "flex", "justify-content": "center", "align-items": "center",
                            "background-color": "#f0f8ff"})
time_frame_next_row = html.Div([
    m5_button,
    html.Div(style={"width": "10px"}),
    m1_button,
    html.Div(style={"width": "10px"}),
    next_button,
], style={"padding": "10px", "display": "flex", "justify-content": "center", "align-items": "center",
          "background-color": "#f0f8ff"})

skip_row_with_all = html.Div([
    auto_button,
    html.Div(style={"width": "10px"}),
    manual_button,
    html.Div(style={"width": "10px"}),
    skip_box,
    html.Div(style={"width": "10px"}),
    skip_button,
    html.Div(style={"width": "10px"}),
    skip_all_button,

], id="to-show", style={"display": "none"})

display_image = html.Div(children=[
    m1_graph,
    m5_graph
], style={"padding": "20px", "border-radius": "5px", "display": "flex",
          "align-items": "center"})
# layout
layout = html.Div([
    html.H1("Back Test", style={
        "text-align": "center",
        "font-size": "32px",
        "color": "#333",
        "font-family": "Helvetica, Arial, sans-serif",
        "border-bottom": "2px solid #333",  # added
        "padding-bottom": "10px",  # added
    }),
    table_div,
    html.Div(style={"height": "10px"}),
    time_frame_next_row,
    html.Div(style={"height": "10px"}),
    skip_row_with_all,
    display_image,
    counter
], style={
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
})


# layout = html.Div([
#     html.H1("Please select the date range from the date picker below to start backtesting."),
#     date_picker,
#     html.Label("Please select the symbol to start backtesting."),
#     symbol_dropdown,
#     account_balance,
#     start_button,
#     html.Hr(),
#     m5_button,
#     m1_button,
#     next_button,
#     html.Div(id="output", children=[
#         auto_button,
#         manual_button,
#         dbc.Row([
#             dbc.Col(skip_box),
#             dbc.Col(skip_button),
#             dbc.Col(skip_all_button)
#         ]),
#         m1_graph,
#         m5_graph
#     ]),
#     html.Div(id="output-2"),
#     counter
# ])


# change timeframe to m1, disabling the m1-button
# enabling the m5-button
@callback([Output(component_id="m1-button", component_property="disabled"),
           Output(component_id="m5-button", component_property="disabled")],
          [Input(component_id="m1-button", component_property="n_clicks"),
           Input(component_id="m5-button", component_property="n_clicks"),
           Input(component_id="start-button", component_property="n_clicks")])
def change_timeframe_m1(m1_click, m5_click, start_click):
    if start_click is None:
        raise PreventUpdate
    if dash.callback_context.triggered_id == "start-button":
        return False, True
    global current_timeframe
    if dash.callback_context.triggered_id == "m1-button":
        current_timeframe = "M1"
        return True, False
    if dash.callback_context.triggered_id == "m5-button":
        current_timeframe = "M5"
        return False, True
    return False, False


# make auto and manual mode visible
@callback(Output(component_id="to-show", component_property="style"),
          Input(component_id="start-button", component_property="n_clicks"))
def update_auto_and_manual_button(n_clicks):
    if n_clicks is None:
        raise PreventUpdate
    return {"padding": "20px", "border-radius": "5px", "display": "flex",
            "align-items": "center", "background-color": "#f0f8ff"}


# change_mode
@callback([Output(component_id="auto-button", component_property="disabled"),
           Output(component_id="manual-button", component_property="disabled"),
           Output(component_id="next-button", component_property="disabled"),
           Output(component_id="counter", component_property="interval")],
          [Input(component_id="manual-button", component_property="n_clicks"),
           Input(component_id="auto-button", component_property="n_clicks"),
           Input(component_id="start-button", component_property="n_clicks")])
def change_mode(manual_click, auto_click, start_click):
    if start_click is None:
        raise PreventUpdate
    global current_mode
    if dash.callback_context.triggered_id == "manual-button" or dash.callback_context.triggered_id == "start-button":
        current_mode = "Manual"
        return False, True, False, 10000000
    current_mode = "Auto"
    return True, False, True, 200


# make skip-time-button disabled
@callback(Output(component_id="skip-button", component_property="disabled"),
          Input(component_id="skip-time", component_property="value"))
def make_skip_button_enabled(value):
    if value is None or value < 1:
        return True
    return False


# make start-button disabled
@callback(
    Output(component_id="start-button", component_property="disabled"),
    [Input(component_id="date-range", component_property="start_date"),
     Input(component_id="date-range", component_property="end_date"),
     Input(component_id="symbol-dropdown", component_property="value"),
     Input(component_id="balance-input", component_property="value")]
)
def update_button_disabled(start_date, end_date, symbol, balance_input):
    if start_date is None or end_date is None or symbol is None:
        raise PreventUpdate
    global previous_end_date, previous_start_date, previous_symbol, previous_balance
    if start_date == previous_start_date and previous_end_date == end_date and symbol == previous_symbol and \
            previous_balance == balance_input:
        return True
    previous_end_date = end_date
    previous_start_date = start_date
    previous_symbol = symbol
    previous_balance = balance_input
    return False


# because the default chart is for m5, hence, m5-button does not need to set the
# disabled property to False
@callback(
    [Output(component_id="m5-graph", component_property="figure"),
     Output(component_id="m5-graph", component_property="style"),
     Output(component_id="m1-graph", component_property="figure"),
     Output(component_id="m1-graph", component_property="style")],
    [Input(component_id="start-button", component_property="n_clicks"),
     Input(component_id="m5-button", component_property="n_clicks"),
     Input(component_id="m1-button", component_property="n_clicks"),
     Input(component_id="next-button", component_property="n_clicks"),
     Input(component_id="counter", component_property="n_intervals"),
     Input(component_id="skip-button", component_property="n_clicks"),
     Input(component_id="skip-all", component_property="n_clicks")],
    [State(component_id="date-range", component_property="start_date"),
     State(component_id="date-range", component_property="end_date"),
     State(component_id="symbol-dropdown", component_property="value"),
     State(component_id="balance-input", component_property="value"),
     State(component_id="skip-time", component_property="value")
     ], config_prevent_initial_callbacks=True
)
def update_output(start_click, m5_click, m1_click, next_click, counter, skip_click, skip_all_click,
                  start_date, end_date, symbol, account_balance, skip_time):
    if start_click is None:
        raise PreventUpdate
    global fig_higher, fig_lower
    if dash.callback_context.triggered_id == "start-button":
        date_format = '%Y-%m-%d'
        start_date = datetime.strptime(start_date, date_format)
        end_date = datetime.strptime(end_date, date_format)
        get_dataset(start_date, end_date, symbol, account_balance)
        return fig_higher, {"display": "block"}, \
               fig_lower, {"display": "none"}
    if dash.callback_context.triggered_id == "m5-button":
        return fig_higher, {"display": "block"}, \
               fig_lower, {"display": "none"}
    if dash.callback_context.triggered_id == "m1-button":
        return fig_higher, {"display": "none"}, \
               fig_lower, {"display": "block"}
    global current_timeframe, current_mode, lower_df
    is_auto_mode = True if current_mode == "Auto" else False
    if dash.callback_context.triggered_id == "next-button" or (
            is_auto_mode and dash.callback_context.triggered_id == "counter"):
        if current_timeframe == "M5":
            for i in range(5):
                append_candles()
            update_graph()
            # print(f"simulation_bot.higher_timeframe.df:{simulation_bot.higher_timeframe.df}")
            # print(f"simulation_bot.lower_timeframe.df:{simulation_bot.lower_timeframe.df}")
            return fig_higher, {"display": "block"}, \
                   fig_lower, {"display": "none"}

        append_candles()
        update_graph()
        return fig_higher, {"display": "none"}, \
               fig_lower, {"display": "block"}
    if dash.callback_context.triggered_id == "skip-button":

        test_skip = skip_time
        if len(lower_df) < test_skip:
            skip_time = len(lower_df)
        for i in range(skip_time):
            append_candles()
        update_graph()
        if current_timeframe == "M5":
            return fig_higher, {"display": "block"}, \
                   fig_lower, {"display": "none"}
        return fig_higher, {"display": "none"}, \
               fig_lower, {"display": "block"}
    if dash.callback_context.triggered_id == "skip-all":
        while len(lower_df) > 0:
            append_candles()
        update_graph()
        if current_timeframe == "M5":
            return fig_higher, {"display": "block"}, \
                   fig_lower, {"display": "none"}
        return fig_higher, {"display": "none"}, \
               fig_lower, {"display": "block"}
    raise PreventUpdate

    # return f"Selected date range: {start_date} to {end_date}\nBalance input is {account_balance}", False, False, False


def get_dataset(start_date, end_date, symbol, account_balance):
    global lower_df, higher_df, simulation_bot, fig_lower, fig_higher
    # start_date = start_date.replace(hour=8)
    end_date = end_date.replace(hour=8)
    # print(f"start_date:{start_date}\nend_date:{end_date}")
    higher_df = pd.DataFrame(mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M5, start_date, end_date))
    lower_df = pd.DataFrame(mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M1, start_date, end_date))
    higher_df["time"] = pd.to_datetime(higher_df["time"], unit="s")
    lower_df["time"] = pd.to_datetime(lower_df["time"], unit="s")
    # print(f"in get_dataset()\nhigher_df:{higher_df}")
    initialize_low, initialize_high = initialize_candles()
    simulation_bot = trading_bot.Bot(symbol, account_balance, lower_df=initialize_low, higher_df=initialize_high)

    update_graph()


def initialize_candles():
    initialize_low = pd.DataFrame()
    initialize_high = pd.DataFrame()
    for i in range(0, 30):
        low_row, high_row = append_candles()
        initialize_low = initialize_low.append(low_row)
        initialize_high = initialize_high.append(high_row)
    initialize_high.reset_index(drop=True, inplace=True)
    initialize_low.reset_index(drop=True, inplace=True)
    return initialize_low, initialize_high


# debug here
def append_candles():
    global lower_df, higher_df, simulation_bot
    if len(lower_df) == 0:
        return [], []
    low_row = lower_df.iloc[0].copy()
    high_row = higher_df.iloc[0].copy()
    low_row_time = low_row["time"].to_pydatetime()
    high_row_time = high_row["time"].to_pydatetime()

    differences = abs(high_row_time - low_row_time)

    if simulation_bot is not None:
        simulation_bot.update(lower_df=low_row, higher_df=high_row)
    if differences >= timedelta(minutes=5):
        higher_df = higher_df.tail(len(higher_df) - 1)
        higher_df.reset_index(drop=True, inplace=True)

    lower_df = lower_df.tail(len(lower_df) - 1)
    lower_df.reset_index(drop=True, inplace=True)
    return low_row, high_row


def update_graph():
    global simulation_bot, fig_lower, fig_higher
    # print("in update_graph")
    if simulation_bot is not None:
        fig_lower = simulation_bot.fig_lower
        fig_higher = simulation_bot.fig_higher
    # print("after assigning fig_lower and fig_higher")
