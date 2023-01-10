import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, use_pages=True)
# app = dash.Dash(__name__)

header_layout = html.Div("Order Block Strategy Forex Trading Robot", style={
    "textAlign": "center",
    "fontSize": "30px",
    "color": "white",
    "fontFamily": "Arial, sans-serif",
    "padding": "20px",
    "borderRadius": "10px",
    "boxShadow": "0 2px 4px rgba(0, 0, 0, 0.2)",
})

navigation_bar = html.Div([
    dcc.Link(
        dbc.Button(page["name"], style={
            "background-color": "lightgreen",
            "color": "white",
            "padding": "10px 20px",
            "border": "none",
            "font-size": "16px",
            "border-radius": "5px",
            "cursor": "pointer",
            "outline": "none",
            "box-shadow": "0 2px 4px rgba(0, 0, 0, 0.2)",
            "font-family": "Georgia, serif",
            "margin-right": "10px",
        }),
        href=page["path"])
    for page in dash.page_registry.values()
], style={
    "display": "flex",
    "alignItems": "center",
    "justifyContent": "center"})

app.layout = html.Div(
    [
        # framework of the app.
        header_layout,
        navigation_bar,
        html.Hr(),
        dash.page_container
    ],style={ "background": "linear-gradient(to right, #006400, #000000)"})

if __name__ == "__main__":
    app.run_server(debug=False)
