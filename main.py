import dash
from dash.dependencies import Input, Output, State, ALL
import dash_core_components as dcc
import dash_html_components as html
import datetime
from flask_caching import Cache
import os
import pandas as pd
import numpy as np
import time
import uuid
import dash_bootstrap_components as dbc
import datetime
import dash_table
import glob


# filtering on category short string labels not working
# drop selection not working
# hist and value counts should be normalized

charts_color = ['#42c8f5', '#543ab0', '#b03a9e', '#e80e3d', '#fff017', '#83ff17', '#17ffd4', '#0793de', '#3e2b80']
files_name = [files for files in glob.iglob('*.csv')]
external_stylesheets = [dbc.themes.GRID, 'assets/topdowndash.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)

cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory',
    'CACHE_THRESHOLD': 200
})

def test_is_cdate(first_val):

    if isinstance(first_val, datetime.datetime):
        return True
    else:
        return False

def test_is_date(first_val):

    if isinstance(first_val, str):
        try :
            pd.to_datetime(first_val)
            return True
        except ValueError:
            return False

def test_no_key_error(dict, key):

    try :
        dict[key]
        return True
    except KeyError:
        return False

def test_is_category(first_val, labels_length):

    if type(first_val) == str:
        return True
    elif labels_length <= 15:
        return True
    else:
        return False

def test_is_int(first_val):

    try :
        int(first_val)
        return True
    except ValueError:
        return False

def identify_type(labels_length, feature_length, first_val):
   
    if test_is_cdate(first_val):
        return 'DateC'

    elif test_is_date(first_val):
        return 'Date'

    elif labels_length == feature_length:
        return 'UniqueID'

    elif test_is_category(first_val, labels_length):
        if labels_length <= 15: ###argh
            return 'CategoryShort'
            
        else:
            return 'CategoryLong'

    elif test_is_int(first_val):
        return 'Numeric'

    else:
        return 'Unknown'

def return_non_none_selection(selection_click, selection_box):

    selection_to_return = [None, None]

    if selection_click is not None:
        for slct in selection_click:
            if slct is not None:
                if test_no_key_error(slct['points'][0], 'pointNumbers'):
                    selection_to_return = ['selection_click_hist', selection_click]

                else:
                    selection_to_return = ['selection_click_bar', selection_click]

    if selection_box is not None:
        for slct in selection_box:
            if slct is not None:
                if test_no_key_error(slct['points'][0], 'pointNumbers'):
                    selection_to_return = ['selection_box_hist', selection_box]

                else:
                    selection_to_return = ['selection_box_bar', selection_box]
    
    return selection_to_return

def read_dataset(filename):

    for sep in [',',';','|']:
            df = pd.read_csv(filename, sep=sep)
            nb_cols = len(df.columns)
            if nb_cols > 1:
                df_size = df.memory_usage(index=True).sum()
                break
    
    return df, df_size

def nb_records_with_na(df):
    
    reccord_contains_na = df.apply(axis=1, func=lambda x: True if (x.isna().sum()>0) else False)
   
    return reccord_contains_na.sum()

def basic_info_dataset(df):
    
    nb_dupli = len(df)
    df.drop_duplicates(inplace=True)
    info_df_dict = {}
    info_df_dict['nb_records_with_na'] = nb_records_with_na(df)
    info_df_dict['selection'] = {}
    info_df_dict['selection'][0] = 'overall'
    info_df_dict['nb_observations'] = nb_dupli
    nb_dupli = nb_dupli - len(df)
    info_df_dict['nb_duplicates'] = nb_dupli
    info_df_dict['nb_var'] = len(df.columns)   
    
    return info_df_dict 


def basic_info_var(var_data):
    
    info_var = {}
    info_var['nb_na'] = len(var_data)
    var_data = var_data.dropna()
    feature_length = len(var_data)
    info_var['nb_na'] = info_var['nb_na'] - feature_length
    nunique_labels = var_data.nunique()
    info_var['type'] = identify_type(nunique_labels, feature_length, var_data.iloc[0])
    info_var['   nunique_labels'] = nunique_labels
    
    return info_var

def stats_info_var(var_data):

    var_stats_info = {}
    var_stats_info['mean'] = round(var_data.mean(), 2)
    var_stats_info['median'] = round(var_data.median(), 2)
    var_stats_info['std'] = round(var_data.std(), 2)
    var_stats_info['max'] = var_data.max()
    var_stats_info['min'] = var_data.min()
    var_stats_info['q1'] = var_data.quantile(q=0.25)
    var_stats_info['q3'] = var_data.quantile(q=0.75)
    ecart_interquartiles = var_stats_info['q3'] - var_stats_info['q1']
    var_stats_info['nb_outliers'] = len(var_data[(var_data < (var_stats_info['q1'] - 1.5*ecart_interquartiles)) | ((var_data > (var_stats_info['q3'] + 1.5*ecart_interquartiles)))])                  
    
    return var_stats_info

def return_filter_ds_based_on_selection(selection, original_dataset, info_df):
    
    slct_var = selection['selected_col']
    slct_on = selection['selection_on_selection']
    type_var_selected = info_df['data'][slct_var]['type']
    df = original_dataset.copy(deep=True)

    if selection['selection_on_chart_type'] == 'hist': #update using last_selection['selection_on_chart_type']
        slct_indexes = selection['indexes_selection']

        if type_var_selected == 'CategoryLong':
            labels = info_df['data'][slct_var]['data'][slct_on].iloc[slct_indexes]['labels'].values # retrive selection index
            df = df[df[slct_var].isin(labels)]

        else:
            df = df.iloc[slct_indexes] # update
    else:
        slct_lbl = selection['selected_labels']
        if selection['selection_type'] == 'box':
            slct_lbl = slct_lbl.split(' and ')

            if type_var_selected in ['Date', 'DateC']:
                df = df[df[slct_var].apply(lambda x: x[:10]).isin(slct_lbl)] 

            elif test_is_int(slct_lbl[0]):
                slct_lbl = [int(lbl) for lbl in slct_lbl] 
                df = df[df[slct_var].isin(slct_lbl)] 

        else:
            if type_var_selected in ['Date', 'DateC']:
                df = df[df[slct_var].apply(lambda x: x[:10]) == slct_lbl]
            else:
                if test_is_int(slct_lbl):
                    slct_lbl = int(slct_lbl)
                df = df[df[slct_var] == slct_lbl] 
            

    return df



def get_dataset(session_id, filename):

    @cache.memoize()
    def query_dataset(session_id, filename):
        dataset, dataset_size = read_dataset(filename)

        return dataset

    return query_dataset(session_id, filename)


def get_info_dataframe(session_id, filename):
    @cache.memoize()
    def query_and_serialize_data(session_id, filename):

        current_time = time.time()
        dataset = get_dataset(session_id, filename)
        info_df = {}
        info_df['data'] = {}
        info_df['info'] = basic_info_dataset(dataset)

        for (name, col_data) in dataset.iteritems():
            info_col = basic_info_var(col_data)

            if info_col['type'] in ['UniqueID', 'Unknown']:
                try:
                    info_df['info'][info_col['type']]
                except KeyError:
                    info_df['info'][info_col['type']] = []

                info_df['info'][info_col['type']].append(name)
            
            else:
                info_col['data'] = {}
                if info_col['type'] in ['CategoryShort', 'CategoryLong','Date', 'DateC']:
                   # if isinstance(col_data.iloc[0], np.int64):
                    #    print(name, 'istype_ind')
                     #   col_data = col_data.astype('object')

                    info_col['data'][0] = col_data.value_counts().reset_index()
                    info_col['data'][0].columns = ['labels', 'count']
                    info_col_stats = stats_info_var(info_col['data'][0]['count'])

                elif info_col['type']  == 'Numeric':
                    info_col['data'][0] = col_data.values
                    info_col_stats = stats_info_var(col_data)

                info_col.update(info_col_stats)                
                info_df['data'][name] = info_col
        
        print('time', time.time()-current_time)
        return info_df

    return query_and_serialize_data(session_id, filename)


def get_filtered_dataframe(session_id, file_name, selection):

    @cache.memoize()
    def filter_data(session_id, file_name, selection):

        selection_copy = selection.copy()
        nb_selection = len(selection_copy.keys())
        if nb_selection>0:
            last_selection = selection_copy.pop(str(nb_selection-1))
            filter_to_apply = True
        else:
            filter_to_apply = False
        
        if len(selection_copy.keys())==0:
            info_df = get_info_dataframe(session_id, file_name)

        else:
            info_df = get_filtered_dataframe(session_id, file_name, selection_copy)

        if filter_to_apply:
            original_dataset = get_dataset(session_id, file_name)
            selection_not_on_overall = True
            while selection_not_on_overall:
                original_dataset = return_filter_ds_based_on_selection(last_selection, original_dataset, info_df)
                if last_selection['selection_on_selection'] == 0:
                    selection_not_on_overall = False

                else:
                    last_selection = selection[last_selection['selection_on_selection']]
   
            
            for var_name in info_df['data'].keys():
                if info_df['data'][var_name]['type'] in ['Date', 'DateC', 'CategoryShort', 'CategoryLong']:
                    info_df['data'][var_name]['data'][nb_selection] = original_dataset[var_name].value_counts().reset_index()
                    info_df['data'][var_name]['data'][nb_selection].columns = ['labels', 'count']
                
                else:
                    info_df['data'][var_name]['data'][nb_selection] = original_dataset[var_name].values

        return info_df
    
    return filter_data(session_id, file_name, selection)


def basic_info_dataset_visual(info):
    top_info = dbc.Row(id='top_short_info', 
                                children = [
                                    dbc.Col([html.H6(str(info['nb_observations'])), html.P('Records')], className='mini_container'),
                                    dbc.Col([html.H6(str(info['nb_var'])), html.P('Variables')], className='mini_container'),
                                    dbc.Col([html.H6(str(info['nb_records_with_na'])), html.P('Records containing NAs')], className='mini_container'),
                                    dbc.Col([html.H6(str(info['nb_duplicates'])), html.P('Duplicated records')], className='mini_container')
                                ])
    
    if test_no_key_error(info, 'UniqueID'):
        top_info.children.append(dbc.Col([html.H6(', '.join(info['UniqueID'])), html.P('Records unique identifier variable')], className='mini_container'))
    
    if test_no_key_error(info, 'Unknown'):
        top_info.children.append(dbc.Col([html.H6(', '.join(info['Unknown'])), html.P('Variables of unrecognized type')], className='mini_container'))
    
    return top_info

def cols_stats_visual(info_data):

    col_tab = ['variable'] + list(info_data.keys())
    tab_val = []
    for info in ['type', 'nb_na', '   nunique_labels', 'mean', 'median', 'std', 'max', 'min', 'q1', 'q3', 'nb_outliers']:
        row_tab = []

        for var in info_data.keys():
            row_tab.append(info_data[var][info])

        tab_val.append([info]+row_tab)

    tab = pd.DataFrame(tab_val, columns=col_tab)
    tab = dash_table.DataTable(id='info_table',
            columns=[{"name": i, "id": i, "selectable": True if i != 'variable' else False} for i in tab.columns],
            data=tab.to_dict('records'),
            column_selectable='multi',
            style_table={
                'maxWidth': '100%',
                'overflowX': 'scroll'
                            })
    return tab


def prepare_info_visu(info_df):

    top_info = basic_info_dataset_visual(info_df['info'])
    tab = cols_stats_visual(info_df['data'])

    return dbc.Container([
                    top_info,
                    dbc.Row(id='selection_radio', className='mini_container'),
                    dbc.Container(id='chart'),
                    dbc.Row(tab, className='mini_container')
                        ])



def serve_layout():

    session_id = str(uuid.uuid4())

    return html.Div([
            dbc.Container([
                dbc.Row(dbc.Col(html.H1('Smoof', style={'textAlign': 'center'}))),
                dbc.Row(dbc.Col(html.H3("Explore your data frictionless", style={'textAlign': 'center'}))),
                html.Br(),
                dbc.Row([dbc.Col(dbc.Container(dbc.Row([dbc.Col(id='col_path_to_dir', children=dcc.Input(size='60', id='path_to_directory', type='text', placeholder='Directory path')), dbc.Col(html.Button(id='directory_entered', children='Go'))]))),dbc.Col(id='file_select_col')]),
                html.Br(),
                dbc.Row(html.Div(id='info_dataset'))
            ], className='body_container'),
            html.Div(id='selection_info', style={'display':'none'}),
            html.Div(session_id, id='session-id', style={'display': 'none'})
            ])


def get_var_chart(var_info, nb_selection_filter, col, selection):

    data = []
    if var_info['type'] == 'CategoryLong':

        for i in range(nb_selection_filter+1):
            dict_data = {'type': 'histogram', 'x': var_info['data'][i]['count'].values,
                        'name': selection[str(i-1)]['selected_col'] + '='  + selection[str(i-1)]['selected_labels'] if i > 0 else 'overall',
                        'marker':{'color':charts_color[i]}}
            data.append(dict_data)
    
    elif var_info['type'] == 'Numeric':
        for i in range(nb_selection_filter+1):
            dict_data = {'type': 'histogram', 'x':var_info['data'][i],
            'name': selection[str(i-1)]['selected_col'] + '='  + selection[str(i-1)]['selected_labels'] if i > 0 else 'overall',
            'marker':{'color':charts_color[i]}}
            data.append(dict_data)

    else:
        for i in range(nb_selection_filter+1):
            dict_data = {'type': 'bar', 'x': var_info['data'][i]['labels'].values,
                        'y':var_info['data'][i]['count'].values,
                        'name': selection[str(i-1)]['selected_col'] + '='  + selection[str(i-1)]['selected_labels'] if i > 0 else 'overall',
                        'marker':{'color':charts_color[i]}}
            data.append(dict_data)      

    return dbc.Row(dbc.Col(className='mini_container', children=dcc.Graph(id={'type':'var_chart', 'index':col}, figure={'data':data, 'layout': {'title': col+' distribution'}})))


def get_tab_category(info_var, nb_selection_filter, col):

    data_table = dash_table.DataTable(id=col+'_table',
                                sort_action='native',
                                columns=[{"name": i, "id": i} for i in info_var['data'][nb_selection_filter].columns],
                                data=info_var['data'][nb_selection_filter].to_dict('records'),
                                style_table={'maxHeight': '500px','overflowY': 'scroll', 'whiteSpace': 'normal','height': 'auto'})
    return data_table


def get_current_selection_visuals(selection):

    options_selection_radio = [{'label':'Overall', 'value':0}]
    options_selection_radio = options_selection_radio + [{'label': values['selected_col'] + ' = ' + values['selected_labels'] , 'value': key} for key, values in selection.items()] #to be replace by info_df['selection'].values
    selection_radio = dbc.Col(dcc.RadioItems(id='radio_items', options= options_selection_radio, value=0,labelStyle={'display': 'inline-block'}))
    drop_selection_filter_button = dbc.Col(html.Button(id='drop_selection_btn', children='Drop selection series', className='mini_container'))

    return [dbc.Row(html.H6('Selection toolbar')), dbc.Row([selection_radio, drop_selection_filter_button])]


def update_selection(selection, type_selection, past_selection, max_index_past_selection, selected_cols, radio_items_selection_value):
    
    if (type_selection != [None, None]) and (type_selection != None):

        type_selection = type_selection.split('_')

        if type_selection[1] == 'click':
            for index, var_selection in enumerate(selection):
                if (var_selection is None) or (var_selection == []):
                    pass

                else:
                    serie = var_selection['points'][0]
                    past_selection[max_index_past_selection] = {}
                    past_selection[max_index_past_selection]['selection_type'] = 'click'
                    past_selection[max_index_past_selection]['selected_col'] = selected_cols[index]
                    past_selection[max_index_past_selection]['selection_on_selection'] = radio_items_selection_value

                    if type_selection[2] == 'bar':
                        past_selection[max_index_past_selection]['selection_on_chart_type'] = 'bar'
                        past_selection[max_index_past_selection]['selected_labels'] = str(serie['label'])

                    else:
                        past_selection[max_index_past_selection]['selection_on_chart_type'] = 'hist'
                        past_selection[max_index_past_selection]['selected_labels'] = str(serie['x'])
                        past_selection[max_index_past_selection]['indexes_selection'] = serie['pointNumbers']

        elif type_selection[1] == 'box':
            for index, var_selection in enumerate(selection):

                if (var_selection is None) or (var_selection == []):
                    pass

                else:
                    past_selection[max_index_past_selection] = {}
                    past_selection[max_index_past_selection]['selection_type'] = 'box'
                    past_selection[max_index_past_selection]['selection_on_selection'] = radio_items_selection_value
                    past_selection[max_index_past_selection]['selected_col'] = selected_cols[index]

                    if type_selection[2] == 'bar':
                        past_selection[max_index_past_selection]['selection_on_chart_type'] = 'bar'
                        labels = ' and '.join([bar['x'] for bar in var_selection['points']])
                        past_selection[max_index_past_selection]['selected_labels'] = labels

                    else:
                        indices_selected = np.concatenate([indices_by_bar['pointNumbers'] for indices_by_bar in var_selection['points']])
                        labels = ' to '.join([str(round(limit, 2)) for limit in var_selection['range']['x']])
                        past_selection[max_index_past_selection]['selection_on_chart_type'] = 'hist'
                        past_selection[max_index_past_selection]['selected_labels'] = labels
                        past_selection[max_index_past_selection]['indexes_selection'] = indices_selected

    return past_selection


@app.callback(Output('file_select_col', 'children'),
                [Input('directory_entered', 'n_clicks')],
                [State('path_to_directory', 'value')])
def display_csv_in_directory(go_n_clicks, directory_path):
    csvs = [csv for csv in glob.iglob(directory_path+'/*.csv')]
    return dcc.Dropdown(id='file_select', options=[{'label':file_name[len(directory_path)+1:], 'value':file_name} for file_name in csvs], value='')


@app.callback([Output('info_dataset', 'children'),
            Output('selection_info', 'children')],
            [Input('file_select', 'value')],
            [State('session-id', 'children')])
def display_info_dataset(file_name, session_id):
    if file_name not in [None, '']:
        info_df = get_info_dataframe(session_id, file_name)
        return prepare_info_visu(info_df), [html.Div({}, id='selection_info_1', style={'display': 'none'}), html.Div({}, id='selection_info_2', style={'display': 'none'})]
    else:
        return dbc.Col(html.H6('Please select a csv file', style={'textAlign': 'center'})),[html.Div({}, id='selection_info_1', style={'display': 'none'}), html.Div({}, id='selection_info_2', style={'display': 'none'})]



@app.callback([Output('chart', 'children'),
            Output('selection_info_1', 'children'),
            Output('selection_radio', 'children')],
            [Input('info_table', 'selected_columns'),
            Input('selection_info_2', 'children')],
            [State('file_select', 'value'), 
            State('session-id', 'children')])
def display_var(cols, selection, file_name, session_id):

    visual_selection = get_current_selection_visuals(selection)

    if cols is not None :
        info_df = get_filtered_dataframe(session_id, file_name, selection)
        charts = []
        nb_selection_filter = len(selection.keys())

        for col in cols:
            charts.append(get_var_chart(info_df['data'][col], nb_selection_filter, col, selection))

            if info_df['data'][col]['type'] == 'CategoryLong':
                charts.append(dbc.Row(dbc.Col(get_tab_category(info_df['data'][col], nb_selection_filter, col), className='mini_container')))
        
        return charts, selection, visual_selection
    else:
        return dbc.Col(html.H6('Please select a variable to display it distribution', style={'textAlign': 'center'})), selection, visual_selection



@app.callback(Output('selection_info_2', 'children'),
                [Input({'type':'var_chart', 'index':ALL}, 'clickData'),
                Input('drop_selection_btn', 'n_clicks'),
                Input({'type':'var_chart', 'index':ALL}, 'selectedData')],
                [State('selection_info_1', 'children'),
                State('radio_items', 'value'),
                State('info_table', 'selected_columns')])
def update_selection_info(selection_click, drop_selection_btn_n_clicks, selection_box, past_selection, radio_items_selection_value, selected_cols):

    max_index_past_selection = len(past_selection.keys())
    
    if drop_selection_btn_n_clicks is not None: 
        del past_selection[radio_items_selection_value]
        current_keys = list(past_selection.keys())
        for i, key in enumerate(current_keys):
            past_selection[str(i)] = past_selection.pop(key)


    type_selection, selection = return_non_none_selection(selection_click, selection_box)
    past_selection = update_selection(selection, type_selection, past_selection, max_index_past_selection, selected_cols, radio_items_selection_value)
        
    return past_selection



app.layout = serve_layout

if __name__ == '__main__':
    app.run_server(debug=True)
