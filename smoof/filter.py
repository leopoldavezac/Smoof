from typing import List, Dict, Union

from dash_bootstrap_components import Col, Row, Button

from smoof.utilities import get_not_none_elements

def get_filter_query(
    click_infos:List,
    box_select_infos:List,
    var_nms:List
    ) -> str:

    FILTER_NM_TO_GET_QUERY = {
        'click':get_query_click,
        'box_select':get_query_box_select
    }

    filter_nm, filter_infos = get_non_null_filter_infos(click_infos, box_select_infos)

    if filter_infos == None:
        return None

    filter_var_nm = get_filter_var_nm(filter_infos, var_nms)
    filter_info = get_not_none_elements(filter_infos)[0]

    return FILTER_NM_TO_GET_QUERY[filter_nm](filter_info, filter_var_nm)


def get_non_null_filter_infos(
    click_infos:List, box_select_infos:List) -> List:

    fiter_nm_to_infos = {
        'click':click_infos,
        'box_select':box_select_infos
    }

    for filter_nm, filter_infos in fiter_nm_to_infos.items():
        if test_filter_infos_is_not_empty(filter_infos):
            return [filter_nm, filter_infos]

    return [None, None]


def test_filter_infos_is_not_empty(filter_infos:List) -> bool:

    if len(filter_infos) == 0:
        return False
    elif len(get_not_none_elements(filter_infos)) == 0:
        return False

    return True


def get_filter_var_nm(filter_infos: List, var_nms:List) -> str:

    for filter_info, var_nm in zip(filter_infos, var_nms):
        if (filter_info != None):
            return var_nm


def get_query_click(filter_info:Dict, var_nm:str) -> str:

    clicked_label = filter_info['points'][0]['label']

    try:
        float(clicked_label)
    except ValueError:
        clicked_label = '"{}"'.format(clicked_label)

    return '{} == {}'.format(var_nm, clicked_label)

def get_query_box_select(filter_info:Dict, var_nm:str) -> str:

    min_val, max_val = filter_info['range']['x']
    min_val, max_val = round(min_val, 2), round(max_val, 2)

    return '({} >= {}) & ({} <= {})'.format(var_nm, min_val, var_nm, max_val)


def get_filters_viz(filter_queries:Union[List[str], None]) -> List[Col]:

    if filter_queries is None:
        return []

    return [Col('filters')] + [
        Col([
            Row(filter_query),
            Row(Button(
                'drop',
                id={'type':'drop_filter', 'index':filter_query},
                class_name='filter')
                )
            ]) for filter_query in filter_queries
    ]

    
