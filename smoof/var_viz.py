
from typing import List, Dict, Union

from pandas import DataFrame, Series, to_datetime

import plotly.graph_objects as go

from dash.dcc import Graph
from dash.dash_table import DataTable
from dash_bootstrap_components import Row, Col


def get_vizualizations(
    trace_dfs: List[DataFrame],
    trace_nms: List[str],
    var_nm_to_type_nm:Dict
    ) -> List[Union[Graph, Row]]:

    TYPE_NM_TO_GET_PLOT_FUNC = {
    'date':get_plot_date,
    'numeric':get_plot_numeric,
    'category_short':get_plot_category_short,
    'category_long':get_plot_category_long
    }

    plots = []

    for var_nm in trace_dfs[0].columns:

        type_nm = var_nm_to_type_nm[var_nm]
        trace_vars = [df[var_nm] for df in trace_dfs]
        plots.append(TYPE_NM_TO_GET_PLOT_FUNC[type_nm](trace_vars, trace_nms))

    return plots


def get_plot_date(trace_vars: List[Series], trace_nms: List[str]) -> Graph:

    fig = go.Figure()

    for trace_nm, trace_var in zip(trace_nms, trace_vars):

        trace_var = to_datetime(trace_var)

        value_counts_series = trace_var.value_counts(normalize=True)
        value_counts_series.sort_index(inplace=True)

        fig.add_trace(
            go.Bar(
                x = value_counts_series.index.values,
                y = value_counts_series.values,
                name=trace_nm
            )
        )

    fig.update_layout(title_text=trace_var.name)

    return Graph(id={'type':'var_chart', 'index':trace_var.name}, figure=fig)


def get_plot_category_short(trace_vars: List[Series], trace_nms: List[str]) -> Graph:

    fig = go.Figure()

    for trace_nm, trace_var in zip(trace_nms, trace_vars):

        value_counts_series = trace_var.value_counts(normalize=True)

        fig.add_trace(
            go.Bar(
                x = value_counts_series.index.values,
                y = value_counts_series.values,
                name = trace_nm
            )
        )

    fig.update_layout(title_text=trace_var.name)

    return Graph(id={'type':'var_chart', 'index':trace_var.name}, figure=fig)


def get_plot_category_long(trace_vars: List[Series], trace_nms: List[str]) -> Graph:

    fig = go.Figure()

    df_trace_vars_value_counts = DataFrame(trace_vars[0].unique().reshape(-1,1), columns=['label'])

    for trace_nm, trace_var in zip(trace_nms, trace_vars):
    
        value_counts_series = trace_var.value_counts(normalize=True)
        value_counts_series.sort_index(inplace=True)

        fig.add_trace(
            go.Histogram(
                x = value_counts_series.values,
                name = trace_nm,
                histnorm = 'probability'
            )
        )

        df_var_val_counts = value_counts_series.to_frame().reset_index()
        df_var_val_counts.columns = ['label', 'perc_{}'.format(trace_nm)]
        df_trace_vars_value_counts = df_trace_vars_value_counts.merge(
            df_var_val_counts, on='label', how='left'
            )

    fig.update_layout(title_text='%s: distribution of value counts' % trace_var.name)
    graph = Graph(id={'type':'var_chart', 'index':trace_var.name}, figure=fig)
    
    table = DataTable(
        sort_action='native',
        columns=[{"name": col_nm, "id": col_nm} for col_nm in df_trace_vars_value_counts.columns],
        data=df_trace_vars_value_counts.to_dict('records'),
        style_table={
            'maxHeight': '500px',
            'overflowY': 'scroll', 
            'whiteSpace': 'normal',
            'height': 'auto'
            }
        )

    return Row([Col(graph), Col(table)])


def get_plot_numeric(trace_vars: List[Series], trace_nms: List[str]) -> Graph:

    fig = go.Figure()

    for trace_nm, trace_var in zip(trace_nms, trace_vars):
        fig.add_trace(
            go.Histogram(
                x = trace_var.values,
                name = trace_nm,
                histnorm = 'probability'
            )
        )

    fig.update_layout(title_text=trace_var.name)
    
    return Graph(id={'type':'var_chart', 'index':trace_var.name}, figure=fig)





