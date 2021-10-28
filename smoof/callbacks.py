from typing import List, Dict, Tuple, Union

from pandas import DataFrame

from dash import Dash
from dash.html import Div, H4
from dash.dependencies import Input, Output, State, ALL
from flask_caching import Cache

from smoof.layout import get_var_nm_dropdow_input
from smoof.load import get_df
from smoof.identify_var_type import get_var_types
from smoof.var_viz import get_vizualizations
from smoof.filter import get_filter_query, get_filters_viz
from smoof.utilities import get_not_none_elements, get_index_not_none_element

def set_callback_load_df(app:Dash, cache:Cache) -> None:

    @app.callback(
        Output('var_nms_dropdown_parent', 'children'),
        [Input('load_df_button', 'n_clicks')],
        [State('path_to_df', 'value')]
    )
    def load_df(_:int, path_to_df:str) -> Div:

        try:

            df = get_df(path_to_df, cache)
            get_var_types(df, cache)

            return get_var_nm_dropdow_input(df.columns.tolist())

        except(FileNotFoundError, ValueError):

            return Div(H4('Please enter a valid file path'))


def set_callback_var_vizs_interactivity(app:Dash, cache:Cache) -> None:

    @app.callback(
        [
            Output('plots_parent', 'children'),
            Output('filter_queries', 'children'),
            Output('filter_queries_viz', 'children')
        ],
        [
            Input('var_nms_dropdown', 'value'),
            Input({'type':'var_chart', 'index':ALL}, 'clickData'),
            Input({'type':'var_chart', 'index':ALL}, 'selectedData'),
            Input({'type':'drop_filter', 'index':ALL}, 'n_clicks')
        
        ],
        [
            State('path_to_df', 'value'),
            State('filter_queries', 'children')
        ]
    )
    def interact(
        var_nms:Union[List[str], None],
        click_infos:List[Union[Dict, None]],
        box_select_infos:List[Union[Dict, None]],
        drop_filter_clicks:List[Union[None, Dict]],
        path_to_df:str,
        filter_queries: List[str]
        ) -> Tuple:

        if var_nms is None:
            return (H4('Select variables to plot'), filter_queries, [])
        
        df = get_df(path_to_df, cache)[var_nms]
        var_nm_to_type_nm = get_var_types(df, cache)

        update_filters_post_drop_filter(drop_filter_clicks, filter_queries)
        update_filters_post_add_filter(click_infos, box_select_infos, var_nms, filter_queries)

        trace_nms = get_trace_nms(filter_queries)
        trace_dfs = get_trace_dfs(filter_queries, df)
        
        filters_viz = get_filters_viz(filter_queries)

        var_vizs = get_vizualizations(trace_dfs, trace_nms, var_nm_to_type_nm)
        
        return (var_vizs, filter_queries, filters_viz)


def update_filters_post_drop_filter(
    drop_filter_clicks:List[Union[int, None]],
    filter_queries:List[str]
    ) -> List[str]:

    if len(get_not_none_elements(drop_filter_clicks)) > 0:
        droped_filter_index = get_index_not_none_element(drop_filter_clicks)
        filter_queries.pop(droped_filter_index)

    return filter_queries


def update_filters_post_add_filter(
    click_infos:List[Union[Dict, None]],
    box_select_infos:List[Union[Dict, None]],
    var_nms:List[Union[str, None]],
    filter_queries:List[str],
    ) -> List[str]:

    filter_query = get_filter_query(click_infos, box_select_infos, var_nms)

    if filter_query:
        filter_queries.append(filter_query)

    return filter_queries


def get_trace_nms(filter_queries:List[str]) -> List[str]:

    return ['overall'] + [filter_query for filter_query in filter_queries]


def get_trace_dfs(filter_queries:List[str], df:DataFrame) -> List[DataFrame]:

    return [df] + [df.query(filter_query) for filter_query in filter_queries]