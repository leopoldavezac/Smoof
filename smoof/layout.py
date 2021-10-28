from typing import List

from dash import html, dcc
import dash_bootstrap_components as dbc

def get_path_to_df_input() -> dbc.Input:

    return dbc.Input(
        id="path_to_df",
        placeholder="Path (from root) to your dataframe",
        type="text",
        style={'width':'100%'}
        )

def get_load_df_button() -> dbc.Button:

    return dbc.Button(
            "load df",
            id="load_df_button",
            className="mr-2",
            n_clicks=0
        )

def get_var_nm_dropdow_input(var_nms: List[str]) -> dcc.Dropdown:

    options = [{'label':var_nm, 'value':var_nm} for var_nm in var_nms]

    return dcc.Dropdown(
        id='var_nms_dropdown',
        options=options,
        value=None,
        multi=True
    )


def serve_layout() -> None:

    return html.Div([
        dbc.Container([
            dbc.Row([
                dbc.Col(get_path_to_df_input()),
                dbc.Col(get_load_df_button()),
            ]),
            dbc.Row([
                dbc.Col(id='var_nms_dropdown_parent')
            ]),
            dbc.Row(id='filter_queries_viz'),
            dbc.Row([
                dbc.Col(id='plots_parent')
            ])
        ]),
        html.Div([], style={'display':'none'}, id='filter_queries')
    ])