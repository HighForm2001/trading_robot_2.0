import os
import pathlib

import dash
import pandas as pd
from dash import html, dcc, Input, Output, callback, dash_table, State
from dash.exceptions import PreventUpdate

excel_path = "excel"
dash.register_page(__name__)
# Get a list of all the files in the directory

delete_button = html.Button(
    id="delete-button",
    children="Delete",
    style={
        "background-color": "red",
        "color": "white",
        "padding": "10px 20px",
        "border": "none",
        "font-size": "16px",
        "border-radius": "5px",
        "cursor": "pointer",
        "outline": "none",
        "box-shadow": "0 2px 4px rgba(0, 0, 0, 0.2)",
    },
)

# layout = html.Div([
#     html.Div([
#         html.H1("This is the record page")
#     ], id="to-change"),
#     dcc.Interval(interval=200, id="counter")
#
# ])

# dropdown boxes
folder_dropdown = dcc.Dropdown(id="folder-select",
                               options=[{"label": folder_name, "value": folder_name, }
                                        for folder_name in os.listdir(excel_path)],
                               style={"min-width": "200px", "width": "flex", "background-color": "#f9f9f9",
                                      "font-size": "16px",
                                      "border-radius": "5px","font-family": "Georgia, serif" })
file_dropdown = dcc.Dropdown(id="file-select",
                             style={"min-width": "200px", "width": "flex", "background-color": "#f9f9f9",
                                    "font-size": "16px", "border-radius": "5px","font-family": "Georgia, serif" }, )
folder_row = html.Div(
    [html.P("Please select the category:",
            style={"font-size": "16px", "font-weight": "bold", "margin-bottom": "10px","font-family": "Georgia, serif" }, ),
     html.Div(style={"width": "10px"}),
     folder_dropdown,
     ],
    style={"padding": "10px",
           "display": "flex",
           "justify-content": "center",
           "align-items": "center",
           "background-color": "#f0f8ff"})
file_row = html.Div(
    [html.P("Please select the report to show:", style={"font-size": "16px",
                                                        "font-weight": "bold", "margin-bottom": "10px",
                                                        "font-family": "Georgia, serif"}
            ),
     html.Div(style={"width": "10px"}),
     file_dropdown],
    style={"padding": "10px",
           "display": "flex",
           "justify-content": "center",
           "align-items": "center",
           "background-color": "#f0f8ff"},
)

rows = html.Div(
    [folder_row, html.Div(style={"width": "30px"}), file_row],
    style={"padding": "10px",
           "display": "flex",
           "justify-content": "center",
           "align-items": "center",
           "background-color": "#f0f8ff"},
)
layout = html.Div(
    [
        html.H1(
            "Report",
            style={
                "text-align": "center",
                "font-size": "32px",
                "color": "#333",
                "font-family": "Helvetica, Arial, sans-serif",
                "border-bottom": "2px solid #333",  # added
                "padding-bottom": "10px",  # added
            },
        ),
        rows,
        html.Div(
            id="table-name",
            style={
                "text-align": "center",
                "font-size": "28px",
                "color": "#00BFFF",
                "padding": "20px",
                "font-family": "Georgia, serif",
            },
        ),
        html.Div(
            id="table-container",
            style={
                "padding": "20px",
                # "backgroundColor": "#FFFFFF",
            },
        ),
        html.Div(
            id="current-file",
            style={"display": "none"},
            children=[delete_button],
        ),
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
    Output(component_id="file-select", component_property="options"),
    Input(component_id="folder-select", component_property="value")
)
def list_files(selected_folder):
    if not selected_folder:
        raise PreventUpdate
    path = pathlib.Path(excel_path, selected_folder)
    return [{"label": file_name, "value": file_name} for file_name in os.listdir(path)]


@callback(
    Output(component_id="table-name", component_property="children"),
    Input(component_id="file-select", component_property="value")
)
def display_file_name(selected_file):
    if not selected_file:
        raise PreventUpdate
    # Extract the file name from the link's id
    return f"Table: {selected_file}", html.Hr(), delete_button


@callback(
    Output(component_id="table-container", component_property="children"),
    Input(component_id="file-select", component_property="value"),
    State(component_id="folder-select", component_property="value")
)
def display_table(selected_file, selected_folder):
    if not selected_file or not selected_folder:
        raise PreventUpdate
    data_path = pathlib.Path(excel_path, selected_folder, selected_file)
    if not os.path.exists(data_path):
        raise PreventUpdate
    # Read the data from the file
    data = pd.read_excel(data_path)
    # Create a data table from the data
    table = dash_table.DataTable(
        columns=[{"name": column, "id": column} for column in data.columns],
        data=data.to_dict("records"),
        style_cell={"textAlign": "center", "backgroundColor": "#FFFFFF", "fontFamily": "Roboto, sans-serif",
                    "padding": "10px"},
        style_data={"border": "1px solid #000000", "color": "#000000"},
        style_header={"backgroundColor": "#000000", "fontWeight": "bold", "color": "#FFFFFF"},
        style_table={"border": "2px solid #000000"},
    )

    return table


@callback(Output(component_id="current-file", component_property="children"),
          Input(component_id="file-select", component_property="value"),
          State(component_id="folder-select", component_property="value"))
def update_current_file(selected_file, selected_folder):
    if not selected_file or not selected_folder:
        raise PreventUpdate
    path = pathlib.Path(excel_path, selected_folder, selected_file)
    return str(path)


@callback(Output(component_id="delete-button", component_property="n_clicks"),
          Input(component_id="delete-button", component_property="n_clicks"),
          State(component_id="current-file", component_property="children")
          )
def delete_report(n_clicks, name):
    if n_clicks is None or not os.path.exists(name):
        raise PreventUpdate
    os.remove(name)
    return n_clicks + 1
#
# # Create a callback to update the list of files when the folder is changed
# @callback(
#     Output('file-links', 'children'),
#     [Input('folder-select', 'value')]
# )
# def update_files(folder):
#     if not folder:
#         raise PreventUpdate
#     global excel_path
#     folder = pathlib.Path(excel_path, folder)
#     # Create a link for each file using a for loop
#     return [html.A(excel_file, href='#', id="file-" + excel_file.replace(".xlsx", "")) for excel_file in
#             os.listdir(folder)]
#
#
# # Create a callback to update the data table when a file is selected
# @callback([Output("table-name", "children"),
#            Output('table-container', 'children'),
#            Output("current-file", 'children')],
#           [Input('file-' + file.replace(".xlsx", ""), 'n_clicks') for roots, subroot, files in os.walk(excel_path) for
#            file in files],
#           Input(component_id="refresh-button",component_property="n_clicks"),
#           [State('file-' + file.replace(".xlsx", ""), 'children') for r, s, files in os.walk(excel_path) for file in
#            files],
#           State(component_id="folder-select", component_property="value"),
#           suppress_callback_exceptions=True
#           )
# def update_table(n_clicks,refresh_click, file, folder):
#     if n_clicks is None or not folder:
#         raise PreventUpdate
#     if dash.callback_context.triggered_id == "refresh-button":
#         raise PreventUpdate
#     global excel_path
#     # Read the Excel file into a Pandas DataFrame
#     file_path = pathlib.Path(excel_path, folder, file)
#     print(f"file_path: {file_path}")
#     df = pd.read_excel(file_path)
#     # Display the DataFrame in a Dash data table
#     return [html.Hr(), html.H1(file), delete_button], \
#            dash_table.DataTable(data=df.to_dict('records')), str(file_path)


# @callback(Output(component_id="to-change", component_property="children"),
#           Input(component_id="counter", component_property="n_intervals"))
# def update_database(n_intervals):
#     global excel_path
#     if not os.path.exists(excel_path):
#         return html.H1("Record not found.")
#     df = pd.read_excel(excel_path)
#     if len(df) < 1:
#         return html.H1("Record not found.")
#     return html.H1("Trading Robot Result: "), dash_table.DataTable(
#         data=df.to_dict("records"),
#         columns=[{"name": col, "id": col} for col in df.columns]
#     )
