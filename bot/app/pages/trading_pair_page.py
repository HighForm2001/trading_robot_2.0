import MetaTrader5 as mt5
import dash
from dash import dcc, html, callback, Output, Input, State, dash_table
from pages.mt5_funcs import get_symbol_names, get_account_info
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

dash.register_page(__name__, path="/")  # '/' is home page
selected_trading_pairs = []
trading_pairs = []
while not trading_pairs:
    trading_pairs = get_symbol_names()
    trading_pairs.sort()
# set trading pair
with open("pages/pair/pair.txt", "w") as f:
    pass

symbol_dropdown = html.Div(
    [html.P("Symbol:", style={"font-weight": "bold"}),
     dcc.Dropdown(id="symbol-dropdown", options=[{'label': symbol, 'value': symbol} for symbol in trading_pairs],
                  placeholder="Please select pairs to trade." if get_symbol_names() else "You are not connected to MetaTrader5",
                  multi=True,
                  style={"width": "200px", "font-size": "16px"},
                  ),
     ],
    style={"padding": "10px"},
)

# get account info
account_info = []
for key, value in get_account_info().items():
    account_info.append({'name': key.title(), 'value': value})

# button
button = html.Button(
    id="confirm-pair",
    children="Start the Bot!",
    disabled=False,
    style={
        "background-color": "lightgreen",
        "border": "none",
        "color": "white",
        "padding": "15px 32px",
        "text-align": "center",
        "text-decoration": "none",
        "display": "inline-block",
        "font-size": "16px",
        "margin": "4px 2px",
        "cursor": "pointer",
    },
)


# page info


# layout
layout = html.Div(
    [
        html.Div(
            [dash_table.DataTable(id="table",
                                  columns=[{"name": "Category", "id": "name"}, {"name": "Info", "id": "value"}],
                                  data=account_info,
                                  sort_mode="single",
                                  sort_action="native",
                                  style_table={
                                      "overflowX": "scroll",
                                      "font-size": "16px",
                                      "table-layout": "fixed",
                                  },
                                  style_header={
                                      "background-color": "rgb(230, 230, 230)",
                                      "font-weight": "bold",
                                  },
                                  style_cell={
                                      "text-align": "center",
                                      "padding": "5px",
                                      "min-width": "100px",
                                  },
                                  style_data_conditional=[
                                      {"if": {"row_index": 0}, "background-color": "rgb(255, 255, 255)",
                                       "color": "rgb(0, 0, 0)", },
                                      {"if": {"row_index": 1}, "background-color": "rgb(242, 242, 242)",
                                       "color": "rgb(0, 0, 0)", }, ],
                                  )
             ]
        ),
        html.Div([
            symbol_dropdown,
            button
        ]),

        html.Div(
            id="status_holder",
            children=[
                dbc.Alert(
                    [
                        html.H3(
                            id="first-line",
                            children="Currently did not select any pair to trade",
                            style={
                                "text-align": "center",
                                "font-size": "20px",
                                "color": "rgb(0, 0, 0)",
                            },
                        ),
                        html.H3(
                            id="second-line",
                            style={
                                "text-align": "center",
                                "font-size": "20px",
                                "color": "rgb(0, 0, 0)",
                            },
                        ),
                        html.H4(
                            id="third-line",
                            children="Trading bot is waiting for your command!",
                            style={
                                "text-align": "center",
                                "font-size": "16px",
                                "color": "rgb(0, 0, 0)",
                            },
                        ),
                    ],
                    color="light",
                ),
            ],
            style={"padding": "20px"},
        ),
        dcc.Interval(id="counter", interval=5000)

    ]
)


# the interaction that will happen when the symbol-dropdown is being interacted by the user.
@callback(
    Output(component_id="confirm-pair", component_property="disabled"),
    Input(component_id="symbol-dropdown", component_property="value"),

)
def proceed_button(s):
    if s:
        return False
    return True


# the behaviour to happen when the confirm button is clicked by the user
@callback([Output(component_id="first-line", component_property="children"),
           Output(component_id="second-line",component_property="children"),
           Output(component_id="third-line",component_property="children")],
          [Input(component_id="confirm-pair", component_property="n_clicks"),
           Input(component_id="counter",component_property="n_intervals")],
          State(component_id="symbol-dropdown", component_property="value"),
          config_prevent_initial_callbacks=True)
def update_holder(n_clicks,n_interval, value):
    global selected_trading_pairs
    if n_clicks == 0:
        raise PreventUpdate
    if dash.callback_context.triggered_id == "confirm-pair":
        if value == selected_trading_pairs:
            raise PreventUpdate
        selected_trading_pairs = value
        with open("pages/pair/pair.txt", "w") as f:
            for x in value:
                f.write(x + "|")
        return "The pair(s) selected to trade: ",\
               'Selected Instrument(s): {}'.format(', '.join(str(v) for v in value)),\
               "Trading bot is looking the chart!"
    elif dash.callback_context.triggered_id == "counter":
        file_value = ""
        with open("pages/pair/pair.txt", "r") as read:
            a = read.readline()
            if a:
                file_value = a.split("|")
        if file_value:
            return "The pair(s) selected to trade: ", 'Selected Instrument(s): {}'.format(
                ', '.join(str(v) for v in file_value)), "Trading bot is looking the chart"
        return "Currently did not select any pair to trade","", "Trading bot is waiting for your command!"


@callback(Output(component_id="confirm-pair", component_property="children"),
          Input(component_id="symbol-dropdown", component_property="value"))
def update_button(value):
    global selected_trading_pairs
    if selected_trading_pairs:
        return "Change Trading Pair!"
    raise PreventUpdate

