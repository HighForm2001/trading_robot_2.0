import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, use_pages=True)
# app = dash.Dash(__name__)

header_layout = html.Div("Order Block Strategy Forex Trading Robot", style={
            "textAlign": "center",
            "fontSize": "30px",
            "color": "blue",
            "backgroundColor": "lightgray"
        })
navigation_bar = html.Div([
            dcc.Link(
                dbc.Button(page["name"], style={
                    "color": "white",
                    "backgroundColor": "blue",
                    "fontSize": "20px",
                    "marginRight": "10px",}),
                href=page["path"])
            for page in dash.page_registry.values()
        ], style={
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "center",
            "backgroundColor": "lightgray"})

app.layout = html.Div(
    [
        # framework of the app.
        header_layout,
        navigation_bar,
        html.Hr(),
        dash.page_container
    ])

if __name__ == "__main__":
    app.run_server(debug=False)
