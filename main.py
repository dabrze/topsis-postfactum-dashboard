# -*- coding: utf-8 -*-
"""Untitled11.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/10o0BmTvgnvn58UdaUywvnWE5CCxrBxNF
"""
import base64
import json
import io
import datetime

import dash
from dash import no_update
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import dash_table
import dash_daq as daq
import pandas as pd
import plotly.express as px

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.UNITED])


def header():
    #TO DO
    #logika przycisków
    return html.Div(children=[
        html.Button('home'),
        html.H3('MSD Transformer app', style={'textAlign' : 'center'}),
        html.Button('information', style={'float' : 'right'})
    ], style={
        'border-bottom-color' : 'black',
        'border-bottom-width' : '5px',
        'border-bottom-style' : 'solid',
        'display' : 'flex',
        'margin' : '20px'
    })


def footer():
    return html.Div(children=[
        html.H1('footer', style={'textAlign' : 'center'})
    ], style={
        'border-top-color' : 'black',
        'border-top-width' : '5px',
        'border-top-style' : 'solid',
        'margin' : '20px'
    })


def home():
    #TO DO
    #dwa przyciski przekierowujące
    pass


def wizard():
    #wydaje się najłatwiej w formie tabów a nie progress bara, na razie nie znalazłem lepszej opcji
    return html.Div(children=[
        dcc.Tabs(vertical=True, children=[
            dcc.Tab(label='data', children=[
                data_loader()
            ],
            id = 'data-loaded'),
            dcc.Tab(label='Parameters', children=[
                parameters_setter()
            ]),
            dcc.Tab(label='Model', children=[
                model_setter()
            ])
        ])
    ])


def data_loader():
    return html.Div([
        html.Div('Upload data'),
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Drag and Drop or Select Files'
            ],
            id = 'upload-data-content'),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            multiple=False
        ),
        html.Div('Upload parameters'),
        dcc.Store(id='stored-params', data=None),
        dcc.Upload(
            id='upload-params',
            children=html.Div([
                'Drag and Drop or Select Files'
            ],
            id = 'upload-params-content'),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            multiple=False
        ),
        html.Div(id='output-datatable-params'),
        html.Div(id='output-datatable'),
    ])


def data_loaded(data):
    return html.Div([
        html.Div('Data Loaded'),
        dash_table.DataTable(
            data=data,
            columns=[{'name': i, 'id': i} for i in list(data[0].keys())],
            page_size=8
        )
    ])


def parse_contents(contents, filename, date):
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
        html.Button(id="submit-button", children="Submit"),
        dcc.Store(id='stored-data', data=df.to_dict('records')),

        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])


def parse_contents_params(contents, filename, date):
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
        dcc.Store(id='stored-params', data=content_dict),

        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])


@app.callback(Output('output-datatable-params', 'children'),
              Output('upload-params-content', 'children'),
              Input('upload-params', 'contents'),
              State('upload-params', 'filename'),
              State('upload-params', 'last_modified'))
def update_load_params(contents_params, name_params, date_params):
    
    if contents_params is not None:
        child = [
            parse_contents_params(c, n, d) for c, n, d in
            zip([contents_params], [name_params], [date_params])]
        return child, name_params
    else:
        raise PreventUpdate


@app.callback(Output('output-datatable', 'children'),
              Output('upload-data-content', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(contents_data, name_data, date_data):

    if contents_data is not None:
        child = [
            parse_contents(c, n, d) for c, n, d in
            zip([contents_data], [name_data], [date_data])]
        return child, name_data   
    else:
        raise PreventUpdate


@app.callback(Output('output-param', 'children'),
              Output('data-loaded', 'children'),
              Input('submit-button','n_clicks'),
              State('stored-data','data'),
              State('stored-params','data'))
def update_parameters(n, data, params):
    if n is None:
        return no_update
    
    if params is None:
        params_labels = ['Weight', 'Expert Min', 'Expert Max', 'Objective']
        criteria = list(data[0].keys())
        
        return html.Div([
            #https://dash.plotly.com/datatable/editable
            dash_table.DataTable(
                id = 'table-edit',
                columns = [{'id': 'Criterion', 'name': 'Criterion'}] + 
                            [{'id': p, 'name': p} for p in params_labels],
                data = [dict(Criterion=i, **{p: 0 for p in params_labels})
                for i in criteria[1:]],
                editable = True
            ),
        ]), data_loaded(data)
    else:
        params_labels = ['Weight', 'Expert Min', 'Expert Max', 'Objective']
        criteria = list(data[0].keys())
        weights = params["Weights"]
        expert_mins = params["Expert Min"]
        expert_maxs = params["Expert Max"]
        objectives = params["Objective"]

        data_params = []

        for id, c in enumerate(criteria[1:]):
            data_params.append(dict(Criterion=c,
                        **{'Weight' : weights[id],
                         'Expert Min' : expert_mins[id],
                         'Expert Max' : expert_maxs[id],
                         'Objective' : objectives[id]}))

        return html.Div([
            #https://dash.plotly.com/datatable/editable
            dash_table.DataTable(
                id = 'table-edit',
                columns = [{'id': 'Criterion', 'name': 'Criterion'}] + 
                            [{'id': p, 'name': p} for p in params_labels],
                data = data_params,
                editable = True
            )
        ]), data_loaded(data)


def parameters_setter():
    return html.Div([
        html.Div(id='output-param')
    ])


def model_setter():
    #https://dash-example-index.herokuapp.com/colourpicker-histogram
    return html.Div([

        html.Div(
            style = {
                'height': '50px',
                'width' : '50px',
                'background-color': '#FF0000'
            }
        ),
        daq.ColorPicker(
            id="color",
            label="Color picker",
            size=164,
            value=dict(hex="#FF0000")
        )
    ])


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


def ranking_vizualization():
    #TO DO
    pass


def improvement_actions():
  #TO DO
  pass


app.layout = html.Div(children=[
    header(),
    wizard(),
    footer()
])

if __name__ == "__main__":
    app.run_server(debug=True)

