"""Untitled11.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/10o0BmTvgnvn58UdaUywvnWE5CCxrBxNF
"""
import base64
import json
import io
#import datetime

import dash
from dash import Dash
from dash import no_update
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from dash import dash_table
import dash_daq as daq
import pandas as pd
import numpy as np
import plotly.express as px
import dash_mantine_components as dmc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUMEN, dbc.icons.FONT_AWESOME])

def header():
    return dbc.Row([
        dbc.Col(dcc.Link(html.I(className="fa fa-home fa-2x", id="css-home-icon"), href='/'), width="auto"),
        dbc.Col(html.H3('MSD Transformer app', id="css-header-title"), width="auto"),
        dbc.Col(dcc.Link(html.I(className="fa fa-info fa-2x", id="css-info-icon"), href='/information'), width="auto")
    ], id="css-header")

def footer():
    github_url = "https://github.com/dabrze/topsis-msd-improvement-actions"
    return dash.html.Footer(children=[
        html.A(html.I(className="fab fa-github fa-2x", id="css-github-icon"), href=github_url, target="_blank"),
        html.Div(html.Img(src="assets/PP_znak_pełny_RGB.png", id="css-logo-img"), id="css-logo-div")
    ], id="css-footer")

def home():
    return html.Div(children=[
        html.Div([
            html.Button(dcc.Link('Load your dataset using WIZARD', href='/show_page_wizard_data_before_submit'), className='big-button'),
            html.Button(dcc.Link('Experiment with ready dataset', href='/main_dash'), className='big-button'),
        ], className='button-container')
    ])

#==============================================================
#   WIZARD
#==============================================================

def wizard():
    return html.Div(children=[
        dcc.Tabs(vertical=True, children=[
            dcc.Tab(label='data', children=[
                show_page_wizard_data_before_submit()
            ],
            id = 'wizard-data-output-data-table'),
            dcc.Tab(label='Parameters', children=[
                show_page_wizard_parameters()
            ]),
            dcc.Tab(label='Model', children=[
                show_page_wizard_model()
            ])
        ])
    ])


def show_page_wizard_data_before_submit():

    return html.Div([
        html.Div('Upload data'),
        html.Div([
            dcc.Upload(
                id='wizard-data-input-upload-data',
                children=html.Div([
                    'Drag and Drop or Select Files'
                ], id = 'wizard-data-output-upload-data-filename'),
                multiple=False
            ),
            html.Div(id='wizard-data-input-remove-data'),
            ], id = 'wizard-data-input-remove-upload-data'),

        html.Div('Upload parameters'),
        html.Div([
            dcc.Store(id='wizard_state_stored-params', data=None),
            dcc.Upload(
                id='wizard-data-input-upload-params',
                children=html.Div([
                    'Drag and Drop or Select Files'
                ], id = 'wizard-data-output-upload-params-filename'),
                multiple=False
            ),
            html.Div(id='wizard-data-input-remove-params'),
            ], id = 'wizard-data-input-remove-upload-params'),

        html.Div(id='wizard-data-output-parsed-data'),
        html.Div(id='wizard-data-output-parsed-params')        
    ])


def show_page_wizard_data_after_submit(data):
    return html.Div([
        html.Div('Data Loaded'),
        dash_table.DataTable(
            data=data,
            columns=[{'name': i, 'id': i} for i in list(data[0].keys())],
            page_size=8
        ),
        html.Button(dcc.Link('Next', href='/parameters'), className='next-button')
    ])


def show_page_wizard_parameters():
    return html.Div([
        html.Div(id='wizard-parameters-output-params-table'),
        html.Div(id = 'wizard-parameters-output-warning', children = ''),
        html.Button(dcc.Link('Back', href='/data'), className='back-button'),
        html.Button(dcc.Link('Next', href='/model'), className='next-button')
    ])


def show_page_wizard_model():
    #https://dash-example-index.herokuapp.com/colourpicker-histogram
    return html.Div([

        html.Div([html.Div(
            style = {
                'height': '50px',
                'width' : '50px',
                'background-color': '#FF0000'
            }
        ),
        daq.ColorPicker(
            label="Color picker",
            size=164,
            value=dict(hex="#FF0000")
        ),
        dcc.RadioItems(['R', 'I','A'], 'R')], id="css-radio-items"),
        html.Button(dcc.Link('Back', href='/parameters'), className='back-button'),
        html.Button(dcc.Link('Finish', href='/main_dash'), className='finish-button')
    ])


@app.callback(Output('wizard-data-output-parsed-data', 'children', allow_duplicate=True),
              Output('wizard-data-output-upload-data-filename', 'children'),
              Output('wizard-data-input-remove-data', 'children', allow_duplicate=True),
              Input('wizard-data-input-upload-data', 'contents'),
              State('wizard-data-input-upload-data', 'filename'),
              State('wizard-data-input-upload-data', 'last_modified'),
              prevent_initial_call=True)
def update_wizard_data_output_data(contents_data, name_data, date_data):

    if contents_data is not None:
        child = [
            parse_file_wizard_data_data(c, n, d) for c, n, d in
            zip([contents_data], [name_data], [date_data])]  
                
        remove = html.Button(id='wizard_data_input_remove-data-button', children='Remove')

        return child, name_data, remove   
    else:
        raise PreventUpdate


@app.callback(Output('wizard-data-input-remove-upload-data', 'children'),
              Output('wizard-data-output-parsed-data', 'children'),
              Output('wizard-data-input-remove-data', 'children'),
              Input('wizard_data_input_remove-data-button','n_clicks'))
def remove_file_wizard_data_data_file(n):
    
    if n is None:
        return no_update

    child =  [
            dcc.Upload(
                id='wizard-data-input-upload-data',
                children=html.Div([
                    'Drag and Drop or Select Files'
                ], id = 'wizard-data-output-upload-data-filename'),
                multiple=False
            ),
            html.Div(id='wizard-data-input-remove-data'),
            ]
    table = None
    remove = None
    return child, table, remove


@app.callback(Output('wizard-data-output-parsed-params', 'children', allow_duplicate=True),
              Output('wizard-data-output-upload-params-filename', 'children'),
              Output('wizard-data-input-remove-params', 'children', allow_duplicate=True),
              Input('wizard-data-input-upload-params', 'contents'),
              State('wizard-data-input-upload-params', 'filename'),
              State('wizard-data-input-upload-params', 'last_modified'),
              prevent_initial_call=True)
def update_wizard_data_output_params(contents_params, name_params, date_params):
    
    if contents_params is not None:
        child = [
            parse_file_wizard_data_params(c, n, d) for c, n, d in
            zip([contents_params], [name_params], [date_params])]
        
        remove = html.Button(id='wizard_data_input_remove-params-button', children='Remove')
        return child, name_params, remove
    else:
        raise PreventUpdate
 

@app.callback(Output('wizard-data-input-remove-upload-params', 'children'),
              Output('wizard-data-output-parsed-params', 'children'),
              Output('wizard-data-input-remove-params', 'children'),
              Input('wizard_data_input_remove-params-button','n_clicks'))
def remove_file_wizard_data_params_file(n):
    
    if n is None:
        return no_update

    child = [
            dcc.Store(id='wizard_state_stored-params', data=None),
            dcc.Upload(
                id='wizard-data-input-upload-params',
                children=html.Div([
                    'Drag and Drop or Select Files'
                ], id = 'wizard-data-output-upload-params-filename'),
                multiple=False
            ),
            html.Div(id='wizard-data-input-remove-params'),
            ]
    table = None
    remove = None
    return child, table, remove


def parse_file_wizard_data_data(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if filename.endswith('.csv'):
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')), sep=';')
        elif filename.endswith('.xls'):
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            return "Please upload a file with the .csv or .xls extension"
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        html.Hr(),

        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns],
            page_size=8
        ),
        html.Button(id="wizard_data_input_submit-button", children="Submit"),
        dcc.Store(id='wizard_state_stored-data', data=df.to_dict('records')),

        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])


def parse_file_wizard_data_params(contents, filename, date):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)

    try:
        if filename.endswith('.json'):
            content_dict = json.loads(decoded)
        else:
            return "Please upload a file with the .json extension"
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    
    return html.Div([
        dcc.Store(id='wizard_state_stored-params', data=content_dict),

        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])


def check_parameters_wizard_data_files(data, params):

    criteria = list(data[0].keys())

    df_data = pd.DataFrame.from_dict(data).set_index(criteria[0])
    df_params = pd.DataFrame.from_dict(params)
    
    n_alternatives = df_data.shape[0]
    m_criteria = df_data.shape[1]

    if "Weights" in df_params:
        if len(df_params["Weights"]) != m_criteria:
            print("Invalid value 'weights'.")
            return -1
        if not all(type(item) in [int, float, np.float64] for item in df_params["Weights"]):
            print("Invalid value 'weights'. Expected numerical value (int or float).")
            return -1
        if not all(item >= 0 for item in df_params["Weights"]):
            print("Invalid value 'weights'. Expected value must be non-negative.")
            return -1
        if not any(item > 0 for item in df_params["Weights"]):
            print("Invalid value 'weights'. At least one weight must be positive.")
            return -1
    else:
        return -1
    
    if "Objective" in df_params:
        if len(df_params["Objective"]) != m_criteria:
            print("Invalid value 'objectives'.")
            return -1
        if not all(item in ["min", "max"] for item in df_params["Objective"]):
            print("Invalid value at 'objectives'. Use 'min', 'max', 'gain', 'cost', 'g' or 'c'.")
            return -1
    else:
        return -1
    
    if "Expert Min" in df_params and "Expert Max" in df_params:
        if len(df_params["Expert Min"]) != m_criteria:
            print("Invalid value at 'expert_range'. Length of should be equal to number of criteria.")
            return -1
        if len(df_params["Expert Max"]) != m_criteria:
            print("Invalid value at 'expert_range'. Length of should be equal to number of criteria.")
            return -1
        if not all(type(item) in [int, float, np.float64] for item in df_params["Expert Min"]):
            print("Invalid value at 'expert_range'. Expected numerical value (int or float).")
            return -1
        if not all(type(item) in [int, float, np.float64] for item in df_params["Expert Max"]):
            print("Invalid value at 'expert_range'. Expected numerical value (int or float).")
            return -1
        
        lower_bound = df_data.min() 
        upper_bound = df_data.max()

        for lower, upper, mini, maxi in zip(lower_bound, upper_bound, df_params["Expert Min"], df_params["Expert Max"]):
            if mini > maxi:
                print("Invalid value at 'expert_range'. Minimal value  is bigger then maximal value.")
                return -1
            if lower < mini:
                print("Invalid value at 'expert_range'. All values from original data must be in a range of expert_range.")
                return -1
            if upper > maxi:
                print("Invalid value at 'expert_range'. All values from original data must be in a range of expert_range.")
                return -1
    else:
        return -1
    
    return 1


def return_columns_wizard_parameters_params_table(params_labels):
    columns = [{
                    'id': 'criterion', 
                    'name': 'Criterion',
                    'type': 'text',
                    'editable': False
                },{
                    'id': params_labels[0], 
                    'name': 'Weight',
                    'type': 'numeric'
                },{
                    'id': params_labels[1], 
                    'name': 'Expert Min',
                    'type': 'numeric'
                },{
                    'id': params_labels[2], 
                    'name': 'Expert Max',
                    'type': 'numeric'
                },{
                    'id': params_labels[3], 
                    'name': 'Objective',
                    'presentation': 'dropdown'                    
                }]
    
    return columns


def fill_parameters_wizard_parameters_params(params, df):

    if params is None:
        m_criteria = df.shape[1]
        return np.ones(m_criteria), df.min(), df.max(), np.repeat('max', m_criteria)
    else:
        return params["Weights"], params["Expert Min"], params["Expert Max"], params["Objective"]


@app.callback(Output('wizard-parameters-output-params-table', 'children', allow_duplicate=True),
              Output('wizard-data-output-data-table', 'children'),
              Input('wizard_data_input_submit-button','n_clicks'),
              State('wizard_state_stored-data','data'),
              State('wizard_state_stored-params','data'),
              prevent_initial_call=True)
def submit_files_wizard_data(n, data, params):
    #https://dash.plotly.com/datatable/reference
    #https://dash.plotly.com/datatable/typing

    if n is None:
        return no_update
    
    if params is not None and check_parameters_wizard_data_files(data, params) == -1:
        print('Prevent update')
    
    params_labels = ['weight', 'expert-min', 'expert-max', 'objective']
    columns = return_columns_wizard_parameters_params_table(params_labels)
    
    criteria = list(data[0].keys())
    df = pd.DataFrame.from_dict(data).set_index(criteria[0])

    weights, expert_mins, expert_maxs, objectives = fill_parameters_wizard_parameters_params(params, df)
    data_params = []

    for id, c in enumerate(criteria[1:]):
        data_params.append(dict(criterion=c,
                    **{params_labels[0] : weights[id],
                    params_labels[1] : expert_mins[id],
                    params_labels[2] : expert_maxs[id],
                    params_labels[3] : objectives[id]}))
        
    #switches = [return_toggle_switch(id, o) for id, o in enumerate(objectives)]

    return html.Div([
        #https://dash.plotly.com/datatable/editable
        #https://community.plotly.com/t/resolved-dropdown-options-in-datatable-not-showing/20366
        dcc.Store(id='wizard_state_stored-data', data=df.to_dict('records')),
        dash_table.DataTable(
            id = 'wizard-parameters-input-parameters-table',
            columns = columns,
            data = data_params,
            editable = True,
            dropdown={
                params_labels[3]: {
                    'options': [
                        {'label': i, 'value': i}
                        for i in ['min', 'max']
                    ],
                    'clearable': False
                },
             }
        ),
        #html.Div(switches)
    ]), show_page_wizard_data_after_submit(data)


def check_updated_params_wizard_parameters(df_data, df_params):
    warnings = []

    #weights
    if (df_params['weight'] < 0).any():
        warnings.append("Weight must be a non-negative number")

    if df_params['weight'].sum() == 0:
        warnings.append("At least one weight must be greater than 0")

    #expert range
    lower_bound = df_data.min() 
    upper_bound = df_data.max()

    for lower, upper, mini, maxi in zip(lower_bound, upper_bound, df_params['expert-min'], df_params['expert-max']):
        if mini > maxi:
            warnings.append("Min value must be lower or equal than max value")
        
        if lower < mini:
            warnings.append("Min value must be lower or equal than the minimal value of given criterion")

        if upper > maxi:
            warnings.append("Max value must be greater or equal than the maximal value of given criterion")
    
    return list(set(warnings))


def parse_warning(warning):
    return html.Div([
        warning
    ])

#Approach 2 - iterate through whole table
@app.callback(Output('wizard-parameters-output-params-table', 'children'),
              Output('wizard-parameters-output-warning', 'children'),
              Input('wizard-parameters-input-parameters-table', 'data_timestamp'),
              State('wizard_state_stored-data','data'),
              State('wizard-parameters-input-parameters-table', 'data'),
              State('wizard-parameters-input-parameters-table', 'data_previous'))
def update_table_wizard_parameters(timestamp, data, params, params_previous):
    #https://community.plotly.com/t/detecting-changed-cell-in-editable-datatable/26219/3
    #https://dash.plotly.com/duplicate-callback-outputs
    params_labels = ['weight', 'expert-min', 'expert-max', 'objective']
    columns = return_columns_wizard_parameters_params_table(params_labels)

    criteria_params = list(params[0].keys())
    
    df_data = pd.DataFrame.from_dict(data)
    df_params = pd.DataFrame.from_dict(params).set_index(criteria_params[0])
     
    warnings = check_updated_params_wizard_parameters(df_data, df_params)
                
    if warnings:
        children = [parse_warning(warning) for warning in warnings]
        params = params_previous
    else:
        children = html.Div([])

    #switches = [return_toggle_switch(id, o) for id, o in enumerate(df_params['objective'])]

    return html.Div([
        #https://dash.plotly.com/datatable/editable
        #https://community.plotly.com/t/resolved-dropdown-options-in-datatable-not-showing/20366
        dcc.Store(id='wizard_state_stored-data', data=data),
        dash_table.DataTable(
            id = 'wizard-parameters-input-parameters-table',
            columns = columns,
            data = params,
            editable = True,
            dropdown={
                params_labels[3]: {
                    'options': [
                        {'label': i, 'value': i}
                        for i in ['min', 'max']
                    ],
                    'clearable': False
                },
             }
        ),
        #html.Div(switches)
    ]), children

'''  
#CHECK PARAMETERS

#Approach 1 - use active cell
@app.callback( Output('wizard-parameters-output-warning', 'children'),
              Input('wizard-parameters-input-parameters-table', 'derived_virtual_row_ids'),
              Input('wizard-parameters-input-parameters-table', 'selected_row_ids'),
              Input('wizard-parameters-input-parameters-table', 'active_cell'),
              State('wizard-parameters-input-parameters-table', 'data'))
def update_table_wizard_parameters(row_ids, selected_row_ids, active_cell, data):
    #https://community.plotly.com/t/input-validation-in-data-table/24026

    criteria = list(data[0].keys())
    df = pd.DataFrame.from_dict(data).set_index(criteria[0])
    print(active_cell)

    warning = "Warning"

    if active_cell:
        warning = df.iloc[active_cell['row']][active_cell['column_id']]

    return html.Div([
        warning
    ])
 
'''

'''
#https://dash.plotly.com/dash-daq/toggleswitch
def return_toggle_switch(id, o):
    switch_id = 'switch-' + str(id)
    objective = True if o == 'max' else False
    return html.Div([
        daq.ToggleSwitch(
            id = switch_id,
            value = objective
        )
    ])
'''
#==============================================================
#   PLAYGROUND
#==============================================================

def main_dash():
    return html.Div(children=[
        dcc.Tabs(children=[
            dcc.Tab(label='Ranking vizualiazation', children=[
                ranking_vizualization()
            ]),
            dcc.Tab(label='Improvement actions', children=[
                improvement_actions()
            ]),
            dcc.Tab(label='analisis of parameters', children=[
                model_setter()
            ])
        ])
    ])

def model_setter():
    pass

def ranking_vizualization():
    #TO DO
    pass

def improvement_actions():
  #TO DO
  pass


#==============================================================
#   MAIN
#==============================================================

app.layout = html.Div(children=[
    header(),
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    footer()
], id="css-layout")


@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/':
        return home()
    elif pathname == '/show_page_wizard_data_before_submit':
    #elif pathname == '/wizard':
        return wizard()
    elif pathname == '/main_dash':
        return main_dash()
    else:
        return '404 - Page not found'


if __name__ == "__main__":
    app.run_server(debug=True)
