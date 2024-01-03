import base64
import json
import io
#import datetime

import csv
import time
import MSDTransformer as msdt
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
import plotly.graph_objects as go
import matplotlib.pyplot as plt

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUMEN, dbc.icons.FONT_AWESOME])

global title
title = "TOPSIS vizualization"

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

def home_layout():
    return html.Div(children=[
        html.Div([
            html.H3('Welcome to WMSD-Transformer!'),
            html.Div('You can start your experiment using wizard'),
            dcc.Link(html.Button('Start WIZARD', className='big-button'), href='/wizard'),
            html.Div('Or find out what this project is about using our example'),
            dcc.Link(html.Button('Experiment with ready dataset', className='medium-button'), href='/main_dash_layout2'),
        ], className='button-container')
    ], id='home-page')

#==============================================================
#   WIZARD
#==============================================================

def wizard():
    return html.Div([
        
        # Data before Submit
        html.Div([
            html.Div([
                html.Div([
                    html.Div(className="progress-bar", children=[
                        html.Div(className="progress-step", children=[
                            html.Div(className="step-circle blue-circle"),
                            html.Div("Upload", className="step-label")
                        ]),
                        html.Div(className="progress-line"),
                        html.Div(className="progress-step", children=[
                            html.Div(className="step-circle"),
                            html.Div("Data", className="step-label")
                        ]),
                        html.Div(className="progress-line"),
                        html.Div(className="progress-step", children=[
                            html.Div(className="step-circle"),
                            html.Div("Parameters", className="step-label")
                        ]),
                        html.Div(className="progress-line"),
                        html.Div(className="progress-step", children=[
                            html.Div(className="step-circle"),
                            html.Div("Model", className="step-label")
                        ]),
                    ])
                ], className='side-bar'),
                html.Div([
                    html.Div([
                        html.Div('Here you can upload your csv file with data and see its preview', className='info'),
                        html.Div('You can also upload parameters file if you already have one or set them later', className='info'),
                        html.Div('If your dataset is not displaying correctly (e.g. whole table is in one column) try to change decimal point or delimiter', className='info'),
                    ], className='info-container'),
                    html.Div([
                        html.Div([
                            html.Div([
                                html.Div('Decimal:'),
                                html.I(className="fa-solid fa-question fa-xs", id='decimal-help'),
                                dbc.Tooltip(
                                    "Enter decimal point in your dataset",
                                    target="decimal-help",
                                ),
                            ], className='css-help'),
                            dcc.Input(id='wizard-data-input-decimal',
                                        type = 'text',
                                        placeholder='.',
                                        minLength=0,
                                        maxLength=1),
                            html.Div([
                                html.Div('Delimiter:'),
                                html.I(className="fa-solid fa-question fa-xs", id='delimiter-help'),
                                dbc.Tooltip(
                                    "Enter delimiter in your dataset",
                                    target="delimiter-help",
                                ),
                            ], className='css-help'),
                            dcc.Input(id='wizard-data-input-delimiter',
                                        type = 'text',
                                        placeholder=',',
                                        minLength=0,
                                        maxLength=1),
                            ], id='input-container'),
                        html.Div([
                            html.Div('Upload data:'),
                            dcc.Store(id='wizard_state_stored-data', data=None),
                            dcc.Upload(
                                id='wizard-data-input-upload-data',
                                children=html.Div([
                                    'Drag and Drop or Select Files'
                                ], id = 'wizard-data-output-upload-data-filename'),
                                multiple=False
                            ),
                            html.Div(id='wizard-data-input-remove-data'),
                            ], id = 'wizard-data-input-remove-upload-data'),

                        html.Div([
                            html.Div('Upload parameters (optional):'),
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
                    ], id="input-upload-container"),

                    html.Div([
                        html.Div(id='wizard-data-output-parsed-data-before'),
                        html.Div(id='wizard-data-output-parsed-params'),
                        html.Div(id='data-preview')
                    ], id='data-preview-content'),
                    html.Div(id='data-table', style={'display': 'none'}),
                    html.Div(html.Button("Submit", id='wizard_data_input_submit-button', className='submit-button', style={'display':'none'}), id='nav-buttons')
                ], className='page-with-side-bar')
            ], className='vertical-page')
        ], id='data_upload_layout', style={'display': 'block'}),


        # Data after Submit
        html.Div([
            html.Div([
                html.Div([
                    html.Div(className="progress-bar", children=[
                        html.Div(className="progress-step", children=[
                            html.Div(className="step-circle"),
                            html.Div("Upload", className="step-label")
                        ]),
                        html.Div(className="progress-line"),
                        html.Div(className="progress-step", children=[
                            html.Div(className="step-circle blue-circle"),
                            html.Div("Data", className="step-label")
                        ]),
                        html.Div(className="progress-line"),
                        html.Div(className="progress-step", children=[
                            html.Div(className="step-circle"),
                            html.Div("Parameters", className="step-label")
                        ]),
                        html.Div(className="progress-line"),
                        html.Div(className="progress-step", children=[
                            html.Div(className="step-circle"),
                            html.Div("Model", className="step-label")
                        ]),
                    ])
                ], className='side-bar'),
                html.Div([
                    html.Div([
                        html.Div('On this page you can view your dataset and set the title for your project', className='info'),
                    ], className ='info-container'),
                    html.Div([
                        html.Div([
                            html.Div([
                                html.Div("project_title", id='wizard-data-input-title'),
                                #html.Button(id='wizard-data-input-title-button', children='title')
                            ], id='wizard-data-after-submit-output-project-title'),
                            html.I(className="fa fa-pen-to-square", id="css-edit-icon"),
                        ], className="css-project-title"),
                        html.Div(id='wizard-data-output-parsed-data-after'),
                    ], id='data-content'),
                    html.Div(html.Button('Next', id='data-to-param', className='next-button'), id='nav-buttons')
                ], className='page-with-side-bar')], className='vertical-page')
        ], id='data_layout', style={'display': 'none'}),

        #Parameters
        html.Div([
            html.Div([
                html.Div([
                    html.Div(className="progress-bar", children=[
                        html.Div(className="progress-step", children=[
                            html.Div(className="step-circle"),
                            html.Div("Upload", className="step-label")
                        ]),
                        html.Div(className="progress-line"),
                        html.Div(className="progress-step", children=[
                            html.Div(className="step-circle"),
                            html.Div("Data", className="step-label")
                        ]),
                        html.Div(className="progress-line"),
                        html.Div(className="progress-step", children=[
                            html.Div(className="step-circle blue-circle"),
                            html.Div("Parameters", className="step-label")
                        ]),
                        html.Div(className="progress-line"),
                        html.Div(className="progress-step", children=[
                            html.Div(className="step-circle"),
                            html.Div("Model", className="step-label")
                        ]),
                    ])
                ], className='side-bar'),
                html.Div([
                    html.Div([
                        html.Div('Now you can view and edit your previously uploaded parameters or automatically generated ones based on dataset values', className='info'),
                    ], className ='info-container'),
                    html.Div(id='wizard-parameters-output-params-table'),
                    html.Div([html.Button('Back', id='param-to-data', className='back-button'),
                    html.Button('Next', id='param-to-model', className='next-button')], id='nav-buttons'),

                    dbc.Modal([
                        dbc.ModalHeader("Warning"),
                        dbc.ModalBody(id='warning-modal-body')
                    ], id='warning-modal', size='sm', centered=True)
                ], className='page-with-side-bar')
            ], className='vertical-page')
        ], id='parameters_layout', style={'display': 'none'}),

        #Model
        html.Div([
            html.Div([
                html.Div([
                    html.Div(className="progress-bar", children=[
                        html.Div(className="progress-step", children=[
                            html.Div(className="step-circle"),
                            html.Div("Upload", className="step-label")
                        ]),
                        html.Div(className="progress-line"),
                        html.Div(className="progress-step", children=[
                            html.Div(className="step-circle"),
                            html.Div("Data", className="step-label")
                        ]),
                        html.Div(className="progress-line"),
                        html.Div(className="progress-step", children=[
                            html.Div(className="step-circle"),
                            html.Div("Parameters", className="step-label")
                        ]),
                        html.Div(className="progress-line"),
                        html.Div(className="progress-step", children=[
                            html.Div(className="step-circle blue-circle"),
                            html.Div("Model", className="step-label")
                        ]),
                    ])
                ], className='side-bar'),
                html.Div([
                    html.Div([
                        html.Div('Here you can select which aggregation function you want to use in TOPSIS ranking', className='info'),
                        html.Div('Additionally you can change the color scale for your plots', className='info'),
                    ], className ='info-container'),
                    html.Div([
                        html.Div([
                            html.Div("Choose aggregation function:"),
                            dcc.RadioItems([
                                {
                                "label":[
                                    html.Span("R: Based on distance from the ideal and anti-ideal solution", className="css-radio-item"),
                                    html.Div(html.Img(src="assets/plotR.png", id="plot-r-img"))
                                ],
                                "value": 'R',
                                },{
                                "label":[
                                    html.Span("I: Based on distance from the ideal solution", className="css-radio-item"),
                                    html.Div(html.Img(src="assets/plotI.png", id="plot-i-img"))
                                ],
                                "value": 'I',
                                },{
                                "label":[
                                    html.Span("A: Based on distance from the anti-ideal solution", className="css-radio-item"),
                                    html.Div(html.Img(src="assets/plotA.png", id="plot-a-img"))
                                ],
                                "value": 'A',
                                },
                            ], value='R', id="wizard-model-input-radio-items"),
                        ], className="css-radio-items"),
                        html.Div([
                            html.Div("Choose color scale for plot:"),
                            dcc.Dropdown(
                                options=px.colors.named_colorscales(),
                                value='jet',
                                clearable=False,
                                id="wizard-model-input-dropdown-color"),
                            dcc.Graph(id='color-preview-output')
                        ], className="css-radio-items"),
                    ], id='model-content'),
                    #https://dash.plotly.com/dash-core-components/radioitems
                    html.Div([
                        html.Button('Back', id='model-to-param', className='back-button'),
                        dcc.Link(html.Button('Finish', className='finish-button'), href='/main_dash_layout')
                    ], id='nav-buttons')
                ], className='page-with-side-bar')
            ], className='vertical-page')
        ], id='model_layout', style={'display': 'none'})
    ])


@app.callback(
    Output("color-preview-output", "figure"), 
    Input("wizard-model-input-dropdown-color", "value"))
def change_colorscale(scale):
    trace = go.Heatmap(z=np.linspace(0, 1, 1000).reshape(1, -1),
                    showscale=False)

    layout = go.Layout(
        height=50,
        width=500,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        clickmode='none'
    )
    trace['colorscale'] = scale
    fig = {'data': [trace], 'layout': layout}
    return fig


@app.callback(Output('model-to-param', 'value'),
              Input('wizard-model-input-radio-items', 'value'),
              Input('wizard-model-input-dropdown-color', 'value'))
def get_agg_fn(agg, colour):
    global agg_g
    global colour_g
    colour_g = colour
    agg_g = agg
    return 'Back'


@app.callback(Output('wizard-data-output-parsed-data-before', 'children', allow_duplicate=True),
              Output('wizard-data-output-parsed-data-after', 'children', allow_duplicate=True),
              Output('wizard-data-output-upload-data-filename', 'children'),
              Output('wizard-data-input-remove-data', 'children', allow_duplicate=True),
              Output('wizard_data_input_submit-button', 'style', allow_duplicate=True),
              Output('wizard-data-input-title', 'children', allow_duplicate=True),
              Input('wizard-data-input-upload-data', 'contents'),
              Input('wizard-data-input-delimiter', 'n_submit'),
              State('wizard-data-input-delimiter', 'value'),
              Input('wizard-data-input-decimal', 'n_submit'),
              State('wizard-data-input-decimal', 'value'),
              State('wizard-data-input-upload-data', 'filename'),
              State('wizard-data-input-upload-data', 'last_modified'),
              prevent_initial_call=True)
def update_wizard_data_output_data(contents_data, enter_del, delimiter, enter_sep, decimal, name_data, date_data):

    if contents_data is not None:
        child = [
            parse_file_wizard_data_data(c, n, d, deli, dec) for c, n, d, deli, dec  in
            zip([contents_data], [name_data], [date_data], [delimiter], [decimal])]  
                
        remove = html.Button(id='wizard_data_input_remove-data-button', className='remove-button', children='Remove')
        project_title = name_data.split('.')[0]

        return child, child, name_data, remove, {'display':'block'}, project_title
    else:
        raise PreventUpdate


@app.callback(Output('wizard-data-input-remove-upload-data', 'children'),
              Output('wizard-data-output-parsed-data-before', 'children'),
              Output('wizard-data-output-parsed-data-after', 'children'),
              Output('wizard-data-input-remove-data', 'children'),
              Output('wizard_data_input_submit-button', 'style'),
              Input('wizard_data_input_remove-data-button','n_clicks'))
def remove_file_wizard_data_data_file(n):
    
    if n is None:
        return no_update

    child =  [
        html.Div('Upload data'),
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
    return child, table, table, remove, {'display':'none'}


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
        
        remove = html.Button(id='wizard_data_input_remove-params-button', className='remove-button', children='Remove')
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
            html.Div('Upload data'),
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

def get_delimiter(data):
    sniffer = csv.Sniffer()
    data = data.decode('utf-8')
    delimiter = sniffer.sniff(data).delimiter
    return delimiter

def parse_file_wizard_data_data(contents, filename, date, delimiter, dec):
    
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    
    if not delimiter:
        delimiter = get_delimiter(decoded)

    if not dec:
        dec = '.'
        
    try:
        if filename.endswith('.csv'):
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')), sep = delimiter, decimal = dec)
            global data 
            data = df
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
        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns],
            style_cell={'textAlign': 'left'},
            page_size=8
        ),
        #html.Button("Submit", id='wizard_data_input_submit-button'),
        #html.Button(id="wizard_data_input_submit-button", children="Submit", n_clicks=0),
        #html.Button('Submit', id='submit-button', n_clicks=0),
        dcc.Store(id='wizard_state_stored-data', data=df.to_dict('records')),
    ])


def parse_file_wizard_data_params(contents, filename, date):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)

    try:
        if filename.endswith('.json'):
            content_dict = json.loads(decoded)
            global params_g
            params_g = content_dict
        else:
            return "Please upload a file with the .json extension"
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    
    return html.Div([
        dcc.Store(id='wizard_state_stored-params', data=content_dict),
    ])


def check_parameters_wizard_data_files(data, params, param_keys):

    criteria = list(data[0].keys())

    df_data = pd.DataFrame.from_dict(data).set_index(criteria[0])
    df_params = pd.DataFrame.from_dict(params)

    n_alternatives = df_data.shape[0]
    m_criteria = df_data.shape[1]

    if param_keys[1] in df_params:
        if len(df_params[param_keys[1]]) != m_criteria:
            print("Invalid value 'weights'.")
            return -1
        if not all(type(item) in [int, float, np.float64] for item in df_params[param_keys[1]]):
            print("Invalid value 'weights'. Expected numerical value (int or float).")
            return -1
        if not all(item >= 0 for item in df_params[param_keys[1]]):
            print("Invalid value 'weights'. Expected value must be non-negative.")
            return -1
        if not any(item > 0 for item in df_params[param_keys[1]]):
            print("Invalid value 'weights'. At least one weight must be positive.")
            return -1
    else:
        return -1
    
    if param_keys[4] in df_params:
        if len(df_params[param_keys[4]]) != m_criteria:
            print("Invalid value 'objectives'.")
            return -1
        if not all(item in ["min", "max"] for item in df_params[param_keys[4]]):
            print("Invalid value at 'objectives'. Use 'min', 'max', 'gain', 'cost', 'g' or 'c'.")
            return -1
    else:
        return -1
    
    if param_keys[2] in df_params and param_keys[3] in df_params:
        if len(df_params[param_keys[2]]) != m_criteria:
            print("Invalid value at 'expert_range'. Length of should be equal to number of criteria.")
            return -1
        if len(df_params[param_keys[3]]) != m_criteria:
            print("Invalid value at 'expert_range'. Length of should be equal to number of criteria.")
            return -1
        if not all(type(item) in [int, float, np.float64] for item in df_params[param_keys[2]]):
            print("Invalid value at 'expert_range'. Expected numerical value (int or float).")
            return -1
        if not all(type(item) in [int, float, np.float64] for item in df_params[param_keys[3]]):
            print("Invalid value at 'expert_range'. Expected numerical value (int or float).")
            return -1
        
        lower_bound = df_data.min() 
        upper_bound = df_data.max()

        for lower, upper, mini, maxi in zip(lower_bound, upper_bound, df_params[param_keys[2]], df_params[param_keys[3]]):
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


def return_columns_wizard_parameters_params_table(param_keys):
    columns = [{
                    'id': 'criterion', 
                    'name': 'Criterion',
                    'type': 'text',
                    'editable': False
                },{
                    'id': param_keys[1], 
                    'name': 'Weight',
                    'type': 'numeric'
                },{
                    'id': param_keys[2], 
                    'name': 'Expert Min',
                    'type': 'numeric'
                },{
                    'id': param_keys[3], 
                    'name': 'Expert Max',
                    'type': 'numeric'
                },{
                    'id': param_keys[4], 
                    'name': 'Objective',
                    'presentation': 'dropdown'                    
                }]
    
    return columns


def fill_parameters_wizard_parameters_params(params, df, param_keys):

    if params is None:
        m_criteria = df.shape[1]
        return np.ones(m_criteria), df.min(), df.max(), np.repeat('max', m_criteria)
    else:
        weights = list(params[param_keys[1]].values())
        mins = list(params[param_keys[2]].values())
        maxs = list(params[param_keys[3]].values())
        objectives = list(params[param_keys[4]].values())

        return weights, mins, maxs, objectives


@app.callback([Output('data-preview', 'children'),
              Output('data-table', 'children', allow_duplicate=True),
              Output('wizard-parameters-output-params-table', 'children', allow_duplicate=True),
              Output('data_upload_layout', 'style', allow_duplicate=True),
              Output('data_layout', 'style', allow_duplicate=True),
              Output('parameters_layout', 'style', allow_duplicate=True),
              Output('model_layout', 'style', allow_duplicate=True)],
              [Input('wizard_data_input_submit-button', 'n_clicks')],
              [State('wizard_state_stored-data', 'data'),
              State('wizard_state_stored-params','data')],
              prevent_initial_call=True)
def submit(n_clicks, data, params):

    param_keys = ['criterion', 'weight', 'expert-min', 'expert-max', 'objective']

    if n_clicks:
        data_preview = dash_table.DataTable(
            data=data,
            columns=[{'name': i, 'id': i} for i in data[0].keys()],
            style_cell={'textAlign': 'left'},
            page_size=8
        )
        data_table = dcc.Store(id='wizard_state_stored-data', data=data)
        if params is not None and check_parameters_wizard_data_files(data, params, param_keys) == -1:
            print('Prevent update')
            return no_update, no_update, no_update, no_update, no_update, no_update, no_update
        
        
        columns = return_columns_wizard_parameters_params_table(param_keys)
        
        criteria = list(data[0].keys())
        df = pd.DataFrame.from_dict(data).set_index(criteria[0])

        weights, expert_mins, expert_maxs, objectives = fill_parameters_wizard_parameters_params(params, df, param_keys)

        data_params = []

        for id, c in enumerate(criteria[1:]):
            data_params.append(dict(criterion=c,
                        **{param_keys[1] : weights[id],
                        param_keys[2] : expert_mins[id],
                        param_keys[3] : expert_maxs[id],
                        param_keys[4] : objectives[id]}))
        
        if not data_params:
            print('Prevent update')
            return no_update, no_update, no_update, no_update, no_update, no_update, no_update
            
        params_table = html.Div([
        #https://dash.plotly.com/datatable/editable
        #https://community.plotly.com/t/resolved-dropdown-options-in-datatable-not-showing/20366
        dash_table.DataTable(
            id = 'wizard-parameters-input-parameters-table',
            columns = columns,
            style_cell={'textAlign': 'left'},
            data = data_params,
            editable = True,
            dropdown={
                param_keys[4]: {
                    'options': [
                        {'label': i, 'value': i}
                        for i in ['min', 'max']
                    ],
                    'clearable': False
                },
             }
        ),
        html.Div("Set all to Min/Max"),
        dcc.Dropdown(['-', 'min', 'max'], '-', id = 'wizard-parameters-input-objectives-dropdown', clearable=False),
        ], className='params-content')
        return (data_preview, data_table, params_table, {'display': 'none'}, {'display': 'block'}, {'display': 'none'}, {'display': 'none'})
    else:
        return no_update, no_update, no_update, no_update, no_update, no_update, no_update


@app.callback([Output('data_upload_layout', 'style', allow_duplicate=True),
              Output('data_layout', 'style', allow_duplicate=True),
              Output('parameters_layout', 'style', allow_duplicate=True),
              Output('model_layout', 'style', allow_duplicate=True)],
              [Input('data-to-param', 'n_clicks')],
              prevent_initial_call=True)
def button_data_params(n_clicks):
    if n_clicks:
        return ({'display': 'none'}, {'display': 'none'}, {'display': 'block'}, {'display': 'none'})
    else:
        return no_update, no_update, no_update, no_update


@app.callback([Output('data_upload_layout', 'style', allow_duplicate=True),
              Output('data_layout', 'style', allow_duplicate=True),
              Output('parameters_layout', 'style', allow_duplicate=True),
              Output('model_layout', 'style', allow_duplicate=True)],
              [Input('param-to-data', 'n_clicks')],
              prevent_initial_call=True)
def button_params_data(n_clicks):
    if n_clicks:
        return ({'display': 'none'}, {'display': 'block'}, {'display': 'none'}, {'display': 'none'})
    else:
        return no_update, no_update, no_update, no_update


@app.callback([Output('data_upload_layout', 'style', allow_duplicate=True),
              Output('data_layout', 'style', allow_duplicate=True),
              Output('parameters_layout', 'style', allow_duplicate=True),
              Output('model_layout', 'style', allow_duplicate=True)],
              [Input('param-to-model', 'n_clicks')],
              prevent_initial_call=True)
def button_params_model(n_clicks):
    if n_clicks:
        return ({'display': 'none'}, {'display': 'none'}, {'display': 'none'}, {'display': 'block'})
    else:
        return no_update, no_update, no_update, no_update


@app.callback([Output('data_upload_layout', 'style', allow_duplicate=True),
              Output('data_layout', 'style', allow_duplicate=True),
              Output('parameters_layout', 'style', allow_duplicate=True),
              Output('model_layout', 'style', allow_duplicate=True)],
              [Input('model-to-param', 'n_clicks')],
              prevent_initial_call=True)
def button_model_params(n_clicks):
    if n_clicks:
        return ({'display': 'none'}, {'display': 'none'}, {'display': 'block'}, {'display': 'none'})
    else:
        return no_update, no_update, no_update, no_update


@app.callback(Output('wizard-data-after-submit-output-project-title', 'children', allow_duplicate=True),
             Input('wizard-data-input-title', 'n_clicks'),
             State('wizard-data-input-title', 'children'),
             prevent_initial_call=True)
def edit_title_wizard_data_after_submit(click, text):
    
    if click:
        return html.Div([
                dcc.Input(id='wizard-data-input-type-title',
                        type = 'text',
                        placeholder=text,
                        minLength=1,
                        maxLength=20),
            ])

    return no_update


@app.callback(Output('wizard-data-after-submit-output-project-title', 'children'),
             Input('wizard-data-input-type-title', 'n_submit'),
             State('wizard-data-input-type-title', 'value'))
def edit_title_wizard_data_after_submit(enter, text):
    
    if enter and text:
        global title
        title = text
        return html.Div([
            html.Div(text, id='wizard-data-input-title')
            ])

    return no_update


def check_updated_params_wizard_parameters(df_data, df_params, param_keys):
    warnings = []

    warning = {
        "text": "",
        "value": "",
        "column": "",
        "row_id": -1
    }
    df_criteria = df_data.drop(columns=df_data.columns[0], axis=1, inplace=False)
    criteria = df_criteria.columns.values.tolist()

    #weights
    if (df_params[param_keys[1]] < 0).any():

        for id, val in enumerate(df_params[param_keys[1]]):
            if val < 0:
                warning['text'] = "Weight must be a non-negative number.\n"
                warning['value'] = val
                warning['column'] = param_keys[1]
                warning['row_id'] = criteria[id]

                warnings.append(warning)

    if df_params[param_keys[1]].sum() == 0:
        warning['text'] = "At least one weight must be greater than 0.\n"
        warning['value'] = 0
        warning['column'] = param_keys[1]
        warning['row_id'] = "each"

        warnings.append(warning)

    #expert range
    lower_bound = df_data.min() 
    upper_bound = df_data.max()



    for id, (lower, upper, mini, maxi) in enumerate(zip(lower_bound[1:], upper_bound[1:], df_params[param_keys[2]], df_params[param_keys[3]])):
        if mini > maxi:
            warning['text'] = "Min value must be lower or equal than max value (" + str(mini) + ").\n"
            warning['value'] = mini
            warning['column'] = param_keys[2]
            warning['row_id'] = criteria[id]
            warnings.append(warning)
        
        if lower < mini:
            warning['text'] = "Min value must be lower or equal than the minimal value of given criterion (" + str(lower) + ").\n"
            warning['value'] = mini
            warning['column'] = param_keys[2]
            warning['row_id'] = criteria[id]
            warnings.append(warning)

        if upper > maxi:
            warning['text'] = "Max value must be greater or equal than the maximal value of given criterion (" + str(upper) + ").\n"
            warning['value'] = maxi
            warning['column'] = param_keys[2]
            warning['row_id'] = criteria[id]
            warnings.append(warning)
    
    #return list(set(warnings))
    return warnings


def parse_warning(warning):

    #print(warning['value'])
    #print(warning['column'])
    #print(warning['row_id'])
    warning2 = warning['text'] + "\n" + "You entered " + "'" + str(warning['value']) + "'" + " in " + "'" + str(warning['column']) + "' column" + " in " + "'" + str(warning['row_id']) + "' row" + ".\n" + "Changes were not applied."

    return warning2

#Approach 2 - iterate through whole table
@app.callback(Output('wizard-parameters-output-params-table', 'children'),
              Output('warning-modal-body', 'children'),
              Output('warning-modal', 'is_open'),
              Input('wizard-parameters-input-parameters-table', 'data_timestamp'),
              Input('wizard-parameters-input-objectives-dropdown', 'value'),
              State('wizard_state_stored-data','data'),
              State('wizard-parameters-input-parameters-table', 'data'),
              State('wizard-parameters-input-parameters-table', 'data_previous'))
def update_table_wizard_parameters(timestamp, objectives_val, data, params, params_previous):
    #https://community.plotly.com/t/detecting-changed-cell-in-editable-datatable/26219/3
    #https://dash.plotly.com/duplicate-callback-outputs


    param_keys = ['criterion', 'weight', 'expert-min', 'expert-max', 'objective']
    columns = return_columns_wizard_parameters_params_table(param_keys)

    criteria_params = list(params[0].keys())
    
    df_data = pd.DataFrame.from_dict(data)
    df_params = pd.DataFrame.from_dict(params).set_index(criteria_params[0])
     
    warnings = check_updated_params_wizard_parameters(df_data, df_params, param_keys)
                
    if warnings:
        warnings_children = [parse_warning(warning) for warning in warnings]
        params = params_previous
        is_open = True
    else:
        warnings_children = html.Div([])
        is_open = False

    if params_previous:
        df_params_prev = pd.DataFrame.from_dict(params_previous).set_index(criteria_params[0])
    
        if not df_params[param_keys[4]].equals(df_params_prev[param_keys[4]]):
            objectives_val = '-'

    if objectives_val != '-':
        for id, val in enumerate(params):
            params[id][param_keys[4]] = objectives_val

    global params_g
    params_g = params

    #switches = [return_toggle_switch(id, o) for id, o in enumerate(df_params['objective'])]

    return html.Div([
        #https://dash.plotly.com/datatable/editable
        #https://community.plotly.com/t/resolved-dropdown-options-in-datatable-not-showing/20366
        dcc.Store(id='wizard_state_stored-data', data=data),
        dash_table.DataTable(
            id = 'wizard-parameters-input-parameters-table',
            columns = columns,
            style_cell={'textAlign': 'left'},
            data = params,
            editable = True,
            dropdown={
                param_keys[4]: {
                    'options': [
                        {'label': i, 'value': i}
                        for i in ['min', 'max']
                    ],
                    'clearable': False
                },
             }
        ),
        html.Div("Set all to Min/Max"),
        dcc.Dropdown(['-', 'min', 'max'], objectives_val, id = 'wizard-parameters-input-objectives-dropdown', clearable=False),
    ]), warnings_children, is_open


@app.callback(Output('wizard-model-output-view', 'children'),
              Input('wizard-model-input-radio-items', 'value'))
def show_view_wizard_model(agg):
    if agg == 'R':
        return html.Div(
                style = {
                    'height': '50px',
                    'width' : '50px',
                    'background-color': '#FF0000'
                    },
                id = "wizard-model-output-view"
            )
    if agg == 'I':
        return html.Div(
                style = {
                    'height': '50px',
                    'width' : '50px',
                    'background-color': '#00FF00'
                    },
                id = "wizard-model-output-view"
            )
    if agg == 'A':
        return html.Div(
                style = {
                    'height': '50px',
                    'width' : '50px',
                    'background-color': '#0000FF'
                    },
                id = "wizard-model-output-view"
            )
    

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

def main_dash_layout2():
    global data
    data = pd.read_csv('bus.csv', sep = ';')
    f = open('bus_params.json')
    params = json.load(f)
    params = pd.DataFrame.from_dict(params)
    params = params.to_dict('records')
    global params_g
    params_g = params
    global agg_g
    agg_g = 'R'
    global colour_g
    colour_g = 'jet'
    return main_dash_layout()

def main_dash_layout():
    global data
    data = data.set_index(data.columns[0])
    if agg_g == 'R':
        buses = msdt.MSDTransformer(msdt.RTOPSIS, 'gurobi')
    elif agg_g == 'A':
        buses = msdt.MSDTransformer(msdt.ATOPSIS, 'gurobi')
    else:
        buses = msdt.MSDTransformer(msdt.ITOPSIS, 'gurobi')
    
    criteria_params = list(params_g[0].keys())
    params = pd.DataFrame.from_dict(params_g).set_index(criteria_params[0])
    buses.fit_transform(data, params['weight'].to_list(), params['objective'].to_list(),  None)
    return html.Div(children=[
        html.Div(id='wizard-data'),
        dcc.Tabs(children=[
            dcc.Tab(label='Ranking visualization', children=[
                html.Div([
                    html.Div('Here is shown your normalized dataset and dataset visualization in WMSD', className='info')
                ], className='info-container'),
                ranking_vizualization(buses)
            ]),
            dcc.Tab(label='Improvement actions', children=[
                html.Div([
                    html.Div('You can use selector of methods to check necessary improvement in chosen alternative to overrank other alternative, and than download a report', className='info')
                ], className='info-container'),
                improvement_actions(buses)
            ]),
            dcc.Tab(label='Analysis of parameters', children=[
                html.Div([
                    html.Div('Here you can analyze and download previously set parameters', className='info')
                ], className='info-container'),
                model_setter()
            ])
        ])
    ])

def model_setter():
    return html.Div(id = 'param-table', children=None)

@app.callback(
        Output('param-table', 'children'),
        Input('param-table', 'value'),
        prevent_initial_call = False
)
def display_parameters(a):
    global params_g
    params = params_g

    params_labels = ['criterion', 'weight', 'expert-min', 'expert-max', 'objective']
    columns = return_columns_wizard_parameters_params_table(params_labels)
    df = pd.DataFrame.from_dict(params)

    return html.Div(id = 'aop-tab', className = 'tab', children=[
        dash_table.DataTable(df.to_dict('records'), [{"name": i, "id": i} for i in df.columns], style_cell={'textAlign': 'left'}),
        html.Button('Download', id='json-download-button'),
        dcc.Download(id='json-download')
    ])

@app.callback(
    Output("json-download", "data"),
    Input("json-download-button", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    df = pd.DataFrame.from_dict(params_g)
    return dcc.send_data_frame(df.to_json, "params.json")


def formating(f):
    return f'{f:.2f}'

def ranking_vizualization(buses):
    df = buses.X_new.sort_values('AggFn', ascending = False).applymap(formating)

    df = df.assign(Rank=None)
    columns = df.columns.tolist()
    columns = columns[-1:] + columns[:-1]
    df = df[columns]

    alternative_names = df.index.tolist()
    for alternative in alternative_names:
        df['Rank'][alternative] = buses._ranked_alternatives.index(alternative) + 1


    df.index.rename('Name', inplace=True)
    df.reset_index(inplace=True)
    fig = buses.plot(plot_name = title, color = colour_g)
    fig.update_layout(clickmode='event+select')
    return html.Div(id = 'rv-tab', className = 'tab', children=[
        dcc.Graph(
            id = 'vizualization',
            figure = fig
        ),
        dash_table.DataTable (
            df.to_dict('records'),
            [{"name": i, "id": i} for i in df.columns],
            style_cell={'textAlign': 'right'},
            sort_action='native',
            id = 'datatable',
            style_table={'overflowX': 'auto'}),
        html.Div(id = 'selected-data')
    ])

'''
@app.callback(
    Output('selected-data', 'children'),
    Input('vizualization', 'selectedData'))
def display_selected_data(selectedData):
    print(selectedData)
    return json.dumps(selectedData, indent=2)
'''
'''
@app.callback(
    Output('selected-data', 'children'),
    Input('vizualization', 'clickData'))
def display_click_data(clickData):
    print(clickData)
    return json.dumps(clickData, indent=2)
'''

def improvement_actions(buses):
    global buses_g
    buses_g = buses
    ids = buses_g.X_new.index
    return html.Div(id = 'ia-tab', className = 'tab', children=[
        dbc.Container([
            html.Div(id = 'viz', children = ranking_vizualization(buses)),
            html.Div([
                html.Div(id = 'ia-options', children=[
                    html.Div(children = ['Improvement action:', 
                        dcc.Dropdown(id = 'choose-method', options=[
                            {'label':method,'value':method}
                            for method in ['improvement_mean', 'improvement_std', 'improvement_features', 'improvement_genetic', 'improvement_single_feature']
                        ],
                        value = 'improvement_mean',
                        clearable = False
                        ),
                    ]),
                    html.Div(children =['Alternative to improve:', dcc.Dropdown(
                        id = 'alternative-to-improve',
                        options = ids
                    )]),
                    html.Div(children = ['Alternative to overcome:', dcc.Dropdown(
                        id = 'alternative-to-overcame',
                        options = ids
                    )]),
                    html.Div(id = 'conditional-settings'),
                    html.Button('Advanced settings', id='advanced-settings', n_clicks=0),
                    html.Div(id = 'advanced-content', children = None),
                    html.Button('Apply', id = 'apply-button', n_clicks=0),
                    html.Div(id = 'improvement-result', children=None),
                    html.Button('Download report', id = 'download-raport', n_clicks=0),
                    html.Div(id = 'download-placeholder')
                ])
            ], id='ia-options-content')
        ], id='ia-tab-content')
    ])

@app.callback(
        Output('download-raport', 'n_clicks'),
        Input('download-raport', 'n_clicks')
)
def report_generation(n):
    if n == 1:
        write_raport()
        return 0
    else:
        return 0

@app.callback(Output('improvement-result', 'children'),
              Input('choose-method', 'value'))
def improvement_result_setup(value):
    name = value +'-result'
    return html.Div(id = name)

@app.callback(
        Output('conditional-settings', 'children'),
        Input('choose-method', 'value')
)
def set_conditional_settings(value):
    features = list(buses_g.X_new.columns[:-3])
    print(features)
    if value =='improvement_features':
        return html.Div(children = [
            'Features to change (features that you allow to change):',
            dcc.Dropdown(
                id = 'features-to-change',
                options = features + ['all'],
                multi = True)
        ])
    elif value == 'improvement_genetic':
        return html.Div(children = [
            'Features to change (features that you allow to change):',
            dcc.Dropdown(
                id = 'features-to-change',
                options = features,
                multi = True)
        ])
    elif value == 'improvement_single_feature':
        return html.Div(children = [
            'feature to change (one feature that you allow to change):',
            dcc.Dropdown(
                id = 'feature-to-change',
                options = features)
        ])

@app.callback(
        Output('features-to-change', 'value'),
        Input('features-to-change', 'value')
)
def all_values(value):
    if value is not None and 'all' in value:
        return list(buses_g.X_new.columns[:-3])
    else:
        return value

@app.callback(
    Output('advanced-content', 'children'),
    Input('choose-method', 'value'),
    Input('advanced-settings', 'n_clicks'),
    prevent_initial_call = False
)
def set_advanced_settings(value, n_clicks):
    if n_clicks % 2 == 0:
        is_hidden = 'hidden'
    else:
        is_hidden = 'visible'
    if value == 'improvement_mean':
        return html.Div(children=[
            html.Div(children=['Improvement ratio (maximum value allowed to be better than desired alternative): ', dcc.Input(
            type = 'number',
            id='improvement-ratio',
            value = 0.000001
            )]),
            html.Div([html.Div('Allow std (True if you allow change in std, False otherwise): '), dcc.Input(
            type = 'text',
            id='allow-std',
            value = 'False'
            )])
        ], style={
            'visibility' : is_hidden,
        })
    elif value == 'improvement_features':
        return html.Div(children=[
            html.Div(children=['Improvement ratio: (maximum value allowed to be better than desired alternative)', dcc.Input(
            type = 'number',
            id='improvement-ratio',
            value=0.000001
            )]),
            html.Div(children=['Boundary values (maximum values of chosen features to be achieved, equal amount as features to change): ', dcc.Input(
            type = 'text',
            id='boundary-values'
            )])
        ], style={
            'visibility' : is_hidden,
        })
    elif value == 'improvement_genetic':
        return html.Div(children = [
            html.Div(children=['Improvement ratio(maximum value allowed to be better than desired alternative): ', dcc.Input(
            type = 'number',
            id='improvement-ratio',
            value = 0.000001
            )]),
            html.Div(children=['Boundary values (maximum values of chosen features to be achieved, equal amount as features to change): ', dcc.Input(
            type = 'text',
            id='boundary-values'
            )]),
            html.Div(children=['Allow deterioration (True if you allow deterioration, False otherwise): ', dcc.Input(
            type = 'text',
            id='allow-deterioration',
            value = 'False'
            )]),
            html.Div([html.Div('Popsize (population size for genetic algorithm): '), dcc.Input(
            type = 'number',
            id='popsize'
            )]),
            html.Div([html.Div('Generations (number of generations in genetic algorithm): '), 
                dcc.Input(
            type = 'number',
            id='generations',
            value = 200
            )])
        ], style={
            'visibility' : is_hidden,
        })
    elif value == 'improvement_single_feature':
        return html.Div(children=[
            html.Div(children=['Improvement ratio (maximum value allowed to be better than desired alternative): ', dcc.Input(
            type = 'number',
            id='improvement-ratio',
            value = 0.000001
            )])
        ], style={
            'visibility' : is_hidden,
        })
    elif value == 'improvement_std':
        return html.Div(children=[
            html.Div([
                html.Div('Improvement ratio (maximum value allowed to be better than desired alternative): '), dcc.Input(
                    type = 'number',
                    id='improvement-ratio',
                    value = 0.000001
            )])
        ], style={
            'visibility' : is_hidden,
        })


@app.callback(
    Output('improvement_genetic-result', 'children'),
    [Input('apply-button', 'n_clicks')],
    #Input('alternative-to-improve', 'value'),
    #Input('alternative-to-overcame', 'value'),
    State('alternative-to-improve', 'value'),
    State('alternative-to-overcame', 'value'),
    State('improvement-ratio', 'value'),
    State('features-to-change', 'value'),
    State('boundary-values', 'value'),
    State('allow-deterioration', 'value'),
    State('popsize', 'value'),
    State('generations', 'value'),
    State('choose-method', 'value'),
    prevent_initial_call = True
)
def improvement_genetic_results(n, alternative_to_imptove, alternative_to_overcame, improvement_ratio, features_to_change, boundary_values, allow_deterioration, popsize, generations, method):    
    global proceed
    proceed = False
    if n>0:
        if boundary_values is not None:
            boundary_values = boundary_values.split(',')
            boundary_values = [float(x) for x in boundary_values]
        if improvement_ratio is None:
            improvement_ratio = 0.000001
        if allow_deterioration is None:
            allow_deterioration = False
        else:
            allow_deterioration = bool(allow_deterioration)
        if generations is None:
            generations = 200
        global improvement
        improvement = buses_g.improvement(method, alternative_to_imptove,alternative_to_overcame, improvement_ratio, features_to_change = features_to_change, boundary_values = boundary_values, allow_deterioration = allow_deterioration, popsize = popsize, n_generations = generations)[:10]
        #rounded_improvement = improvement.apply(formating)
        #rounded_improvement = [row.applymap(formating) for index, row in improvement.iterrows()]
        rounded_improvement = improvement.apply(np.vectorize(formating))
        global improvement_parameters
        improvement_parameters = {'parameters':['method', 'alternative_to_imptove', 'alternative_to_overcame', 'improvement_ratio', 'features_to_change', 'boundary_values', 'allow_deterioration', 'popsize', 'generations'], 'values':[method, alternative_to_imptove, alternative_to_overcame, improvement_ratio, features_to_change, boundary_values, allow_deterioration, popsize, generations]}
        proceed = True
        return dash_table.DataTable(rounded_improvement.to_dict('records'), [{"name": i, "id": i} for i in rounded_improvement.columns], style_cell={'textAlign': 'left'}, style_table={'overflowX': 'auto'})
    else:
        proceed = True
        raise PreventUpdate

@app.callback(
    Output('improvement_features-result', 'children'),
    [Input('apply-button', 'n_clicks')],
    #Input('alternative-to-improve', 'value'),
    #Input('alternative-to-overcame', 'value'),
    State('alternative-to-improve', 'value'),
    State('alternative-to-overcame', 'value'),
    State('improvement-ratio', 'value'),
    State('features-to-change', 'value'),
    State('boundary-values', 'value'),
    State('choose-method', 'value'),
    prevent_initial_call = True
)
def improvement_features_results(n, alternative_to_imptove, alternative_to_overcame, improvement_ratio, features_to_change, boundary_values, method):    
    global proceed
    proceed = False
    if boundary_values is not None:
        boundary_values = boundary_values.split(',')
        boundary_values = [float(x) for x in boundary_values]
    if n>0:
        if improvement_ratio is None:
            improvement_ratio = 0.000001
        global improvement
        improvement = buses_g.improvement(method, alternative_to_imptove,alternative_to_overcame, improvement_ratio, features_to_change = features_to_change, boundary_values = boundary_values)
        rounded_improvement = improvement.applymap(formating)
        proceed = True
        return dash_table.DataTable(rounded_improvement.to_dict('records'), [{"name": i, "id": i} for i in rounded_improvement.columns], style_cell={'textAlign': 'left'}, style_table={'overflowX': 'auto'})
    else:
        proceed = True
        raise PreventUpdate
    
@app.callback(
    Output('improvement_single_feature-result', 'children'),
    [Input('apply-button', 'n_clicks')],
    #Input('alternative-to-improve', 'value'),
    #Input('alternative-to-overcame', 'value'),
    State('alternative-to-improve', 'value'),
    State('alternative-to-overcame', 'value'),
    State('improvement-ratio', 'value'),
    State('feature-to-change', 'value'),
    State('choose-method', 'value'),
    prevent_initial_call = True
)
def improvement_feature_results(n, alternative_to_imptove, alternative_to_overcame, improvement_ratio, feature_to_change, method):    
    global proceed
    proceed = False
    if n>0:
        if improvement_ratio is None:
            improvement_ratio = 0.000001
        global improvement
        improvement = buses_g.improvement(method, alternative_to_imptove,alternative_to_overcame, improvement_ratio, feature_to_change = feature_to_change)
        rounded_improvement = improvement.applymap(formating)
        proceed = True
        return dash_table.DataTable(rounded_improvement.to_dict('records'), [{"name": i, "id": i} for i in rounded_improvement.columns], style_cell={'textAlign': 'left'}, style_table={'overflowX': 'auto'})
    else:
        proceed = True
        raise PreventUpdate
    

@app.callback(
    Output('improvement_mean-result', 'children'),
    [Input('apply-button', 'n_clicks')],
    #Input('alternative-to-improve', 'value'),
    #Input('alternative-to-overcame', 'value'),
    State('alternative-to-improve', 'value'),
    State('alternative-to-overcame', 'value'),
    State('improvement-ratio', 'value'),
    State('allow-std', 'value'),
    State('choose-method', 'value'),
    prevent_initial_call = True
)
def improvement_mean_results(n, alternative_to_imptove, alternative_to_overcame, improvement_ratio, allow_std, method):    
    global proceed
    proceed = False
    if n>0:
        if improvement_ratio is None:
            improvement_ratio = 0.000001
        if allow_std is None:
            allow_std = False
        else:
            if allow_std == 'True':
                allow_std = True
            else:
                allow_std = False
        global improvement
        improvement = buses_g.improvement(method, alternative_to_imptove,alternative_to_overcame, improvement_ratio, allow_std = allow_std)
        rounded_improvement = improvement.applymap(formating)
        criteria_params = list(params_g[0].keys())
        params = pd.DataFrame.from_dict(params_g).set_index(criteria_params[0])
        raport = f'''
            <html>
                <head>
                    <title>Topsis Improvement Actions Report</title>
                </head>
                <body>
                    <h1>Dataset</h1>
                    {data.to_html()}
                    <h1>parameters</h1>
                    {params.to_html()}
                    <img src='chart.png' width="700">
                </body>
            </html>
        '''
        with open('html_report.html', 'w') as f:
            f.write(raport)
        proceed = True
        return dash_table.DataTable(rounded_improvement.to_dict('records'), [{"name": i, "id": i} for i in rounded_improvement.columns], style_cell={'textAlign': 'left'}, style_table={'overflowX': 'auto'})
    else:
        proceed = True
        raise PreventUpdate
    

@app.callback(
    Output('improvement_std-result', 'children'),
    [Input('apply-button', 'n_clicks')],
    #Input('alternative-to-improve', 'value'),
    #Input('alternative-to-overcame', 'value'),
    State('alternative-to-improve', 'value'),
    State('alternative-to-overcame', 'value'),
    State('improvement-ratio', 'value'),
    State('choose-method', 'value'),
    prevent_initial_call = True
)
def improvement_std_results(n, alternative_to_imptove, alternative_to_overcame, improvement_ratio, method):    
    global proceed
    proceed = False
    if n>0:
        if improvement_ratio is None:
            improvement_ratio = 0.000001
        global improvement
        improvement = buses_g.improvement(method, alternative_to_imptove,alternative_to_overcame, improvement_ratio)
        rounded_improvement = improvement.applymap(formating)
        proceed = True
        return dash_table.DataTable(rounded_improvement.to_dict('records'), [{"name": i, "id": i} for i in rounded_improvement.columns], style_cell={'textAlign': 'left'}, style_table={'overflowX': 'auto'})
    else:
        proceed = True
        raise PreventUpdate

'''
@app.callback(
    Output('improvement-result', 'children'),
    [Input('apply-button', 'n_clicks')],
    #Input('alternative-to-improve', 'value'),
    #Input('alternative-to-overcame', 'value'),
    State('alternative-to-improve', 'value'),
    State('alternative-to-overcame', 'value'),
    State('features-to-change', 'value'),
    State('improvement-ratio', 'value'),
    State('choose-method', 'value'),
    prevent_initial_call = True
)
def improvement_results(n, alternative_to_imptove, alternative_to_overcame, features_to_change,improvement_ratio, method):
    print(features_to_change)
    
    if n>0:
        global improvement
        improvement = buses_g.improvement(method, alternative_to_imptove,alternative_to_overcame)
        return dash_table.DataTable(improvement.to_dict('records'), [{"name": i, "id": i} for i in improvement.columns])
    else:
        raise PreventUpdate
'''

def write_raport():
    criteria_params = list(params_g[0].keys())
    params = pd.DataFrame.from_dict(params_g).set_index(criteria_params[0])
    raport = f'''
        <html>
            <head>
                <title>Topsis Improvement Actions Report</title>
            </head>
            <body>
                <h1>{title}</h1>
                <p>Data used in experiment</p>
                {data.to_html()}
                <p>data parameters used in experiment</p>
                {params.to_html()}
                <p>vizualization of performed improvement</p>
                <img src='chart.png' width="100%">
                <p>values necessary to improve</p>
                {improvement.to_html()}
                <p>parameters of improvement algorithm</p>
                {pd.DataFrame.from_dict(improvement_parameters).to_html()}
            </body>
        </html>
    '''
    with open('html_report.html', 'w') as f:
        f.write(raport)

@app.callback(
    Output('viz', 'children'),
    [Input('apply-button', 'n_clicks')],
    #Input('alternative-to-improve', 'value'),
    State(component_id='alternative-to-improve', component_property='value'),
    prevent_initial_call = True
)
def vizualization_change(n, alternative_to_imptove):
    time.sleep(0.5)
    while True:
        if proceed:
            break
        time.sleep(0.5)
    if n>0:
        df = buses_g.X_new.sort_values('AggFn', ascending = False).applymap(formating)

        df = df.assign(Rank=None)
        columns = df.columns.tolist()
        columns = columns[-1:] + columns[:-1]
        df = df[columns]

        alternative_names = df.index.tolist()
        for alternative in alternative_names:
            df['Rank'][alternative] = buses_g._ranked_alternatives.index(alternative) + 1

        df.index.rename('Name', inplace=True)
        df.reset_index(inplace=True)
        #a = buses_g.plot(plot_name = title, color = colour_g)
        fig = buses_g.plot2(alternative_to_imptove, improvement)
        fig.write_image("chart.png")
        return html.Div(children=[
            dcc.Graph(
                id = 'vizualization',
                figure = fig
            ),
            dash_table.DataTable(df.to_dict('records'), [{"name": i, "id": i} for i in df.columns], sort_action='native', style_cell={'textAlign': 'left'}, style_table={'overflowX': 'auto'})
        ])
    else:
        raise PreventUpdate


#==============================================================
#   MAIN
#==============================================================

app.layout = html.Div(children=[
    header(),
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    dcc.Store(id='data-store', storage_type='memory'),
    dcc.Store(id='params-store', storage_type='memory'),
    footer()
], id="css-layout")


@app.callback(Output('page-content', 'children', allow_duplicate=True),
              Input('url', 'pathname'),
              prevent_initial_call=True)
def display_page(pathname):
    if pathname == '/':
        return home_layout()
    elif pathname == '/wizard':
        return wizard()
    elif pathname == '/main_dash_layout':
        return main_dash_layout()
    elif pathname == '/main_dash_layout2':
        return main_dash_layout2()
    else:
        return '404 - Page not found'

def parse_args():
    from argparse import ArgumentParser
    from argparse import ArgumentDefaultsHelpFormatter

    parser = ArgumentParser(description="WMSD Dashboard server.", formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("--ip", type=str, default="127.0.0.1", help="The IP address the WMSD Dashboard server will listen on.")
    parser.add_argument("--port", type=int, default=8050, help="The port the WMSD Dashboard server will listen on")
    parser.add_argument("--solver", type=str, default="scip", help="The nonlinear programming solver used to calculate the upper perimeter of the WMSD space.")
  

    args = parser.parse_args()

    return args

if __name__ == "__main__":
    args = parse_args()
    app.run_server(debug=True, host=args.ip, port=args.port)