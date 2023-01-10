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


# symbol_dropdown = html.Div(
#     [html.P("Symbol:", style={"font-weight": "bold"}),
#      dcc.Dropdown(id="symbol-dropdown", options=[{'label': symbol, 'value': symbol} for symbol in trading_pairs],
#                   placeholder="Please select pairs to trade." if get_symbol_names() else "You are not connected to MetaTrader5",
#                   multi=True,
#                   style={"width": "200px", "font-size": "16px"},
#                   ),
#      ],
#     style={"padding": "10px"},
# )


def extract_account_info():
    to_return = []
    for key, value in get_account_info().items():
        to_return.append({'name': key.title(), 'value': value})
    return to_return


# get account info
account_info = extract_account_info()

# button
button = html.Button(
    id="confirm-pair",
    children="Start the Bot!",
    disabled=False,
    style={
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
    },
)

symbol_dropdown = html.Div(
    [html.P("Symbol:",
            style={"font-weight": "bold", "font-size": "16px", "color": "#333", "font-family": "Georgia, serif",
                   "margin-right": "10px", }),
     html.Div(style={"width": "10px"}),
     dcc.Dropdown(id="symbol-dropdown",
                  placeholder="Symbols" if get_symbol_names() else "You are not connected to MetaTrader5",
                  options=[{'label': symbol, 'value': symbol} for symbol in trading_pairs],
                  multi=True,
                  style={"width": "flex", "min-width": "200px", "font-family": "Georgia, serif"}, ),
     html.Div(style={"width": "10px"}),  # This adds a 10px wide space between the Dropdown and button
     button],
    style={"padding": "10px", "display": "flex", "justify-content": "center", "align-items": "center",
           "background-color": "#f0f8ff"},
)

dataTable = dash_table.DataTable(
    id="table",
    columns=[{"name": "Category", "id": "name"}, {"name": "Info", "id": "value"}],
    data=account_info,
    sort_mode="single",
    sort_action="native",
    style_table={
        "overflowX": "scroll",
        "font-size": "16px",
        "font-family": "Arial, sans-serif",
        "color": "#333",
        "background-color": "#fff",
        "table-layout": "fixed",
    },
    style_header={
        "background-color": "rgb(230, 230, 230)",
        "font-weight": "bold",
        "text-align": "center",
        "color": "#333",
    },
    style_cell={
        "text-align": "center",
        "padding": "5px",
        "min-width": "100px",
        "color": "#333",
    },
    style_data_conditional=[
        {
            "background-color": "rgb(255, 255, 255)",
            "color": "rgb(0, 0, 0)",
        },
        {
            "background-color": "rgb(242, 242, 242)",
            "color": "rgb(0, 0, 0)",
        },
    ],
)
table_div = html.Div(
    dataTable,
    style={"padding": "10px", "display": "flex", "justify-content": "center", "align-items": "center",
           "background-color": "#f0f8ff","font-family": "Georgia, serif"},
)

# page info

# layout
layout = html.Div(
    [
        table_div,
        html.Div(style={"height": "10px"}),
        symbol_dropdown,
        html.Div(style={"height": "10px"}),
        html.Div(
            id="status_holder",
            children=[
                html.H3(id="first-line", children="Currently did not select any pair to trade",
                        style={
                            "text-align": "center",
                            "font-size": "20px",
                            "color": "rgb(0, 0, 0)",
                            "font-family": "Georgia, serif",
                            "margin-bottom": "10px",
                        },
                        ),
                html.H3(id="second-line", style={
                    "text-align": "center",
                    "font-size": "20px",
                    "color": "rgb(0, 0, 0)",
                    "font-family": "Georgia, serif",
                    "margin-bottom": "10px",
                },
                        ),
                html.H4(id="third-line", children="Trading bot is waiting for your command!",
                        style={
                            "text-align": "center",
                            "font-size": "16px",
                            "color": "rgb(0, 0, 0)",
                            "font-family": "Georgia, serif",
                        },
                        ),
            ],
            style={"padding": "10px", "justify-content": "center", "align-items": "center",
                   "background-color": "#f0f8ff"},
        ),
        dcc.Interval(id="counter", interval=5000)
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
    }
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
           Output(component_id="second-line", component_property="children"),
           Output(component_id="third-line", component_property="children")],
          [Input(component_id="confirm-pair", component_property="n_clicks"),
           Input(component_id="counter", component_property="n_intervals")],
          State(component_id="symbol-dropdown", component_property="value"),
          config_prevent_initial_callbacks=True)
def update_holder(n_clicks, n_interval, value):
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
        return "The pair(s) selected to trade: ", \
               'Selected Instrument(s): {}'.format(', '.join(str(v) for v in value)), \
               "Trading bot is looking the chart!"
    elif dash.callback_context.triggered_id == "counter":
        file_value = ""
        with open("pages/pair/pair.txt", "r") as read:
            a = read.readline()
            if a:
                file_value = a.split("|")
        if file_value:
            return "The pair(s) selected to trade: ", 'Selected Instrument(s): {}'.format(
                ', '.join(str(v) for v in file_value))[:-2], "Trading bot is looking the chart!"
        return "Currently did not select any pair to trade", "", "Trading bot is waiting for your command!"


@callback(Output(component_id="table", component_property="data"),
          Input(component_id="counter", component_property="n_intervals"))
def update_table(n_intervals):
    return extract_account_info()


@callback(Output(component_id="confirm-pair", component_property="children"),
          Input(component_id="symbol-dropdown", component_property="value"))
def update_button(value):
    global selected_trading_pairs
    if selected_trading_pairs:
        return "Change Trading Pair!"
    raise PreventUpdate
