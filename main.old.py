import json
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

import time
import WMSDTransformer as wmsdt
import dash
from dash import no_update
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from dash import dash_table
from common.layout_elements import (
    EXTERNAL_STYLESHEETS,
    EXTERNAL_SCRIPTS,
    header,
    footer,
)
from pages import criteria, home, upload


app = dash.Dash(
    __name__,
    external_stylesheets=EXTERNAL_STYLESHEETS,
    external_scripts=EXTERNAL_SCRIPTS,
    suppress_callback_exceptions=True,
)

global title
title = "Postfactum Analysis Dashboard"


# ==============================================================
#   WIZARD
# ==============================================================


def wizard():
    return html.Div(
        [
            # Parameters
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Div(
                                                "Now you can view and edit your previously uploaded parameters or automatically generated ones based on dataset values",
                                                className="info",
                                            ),
                                        ],
                                        className="info-container",
                                    ),
                                    html.Div(
                                        id="wizard-parameters-output-params-table"
                                    ),
                                    html.Div(
                                        [
                                            html.Button(
                                                "Back",
                                                id="param-to-data",
                                                className="back-button",
                                            ),
                                            html.Button(
                                                "Next",
                                                id="param-to-model",
                                                className="next-button",
                                            ),
                                        ],
                                        id="nav-buttons",
                                    ),
                                    dbc.Modal(
                                        [
                                            dbc.ModalHeader("Warning"),
                                            dbc.ModalBody(id="warning-parameters-body"),
                                        ],
                                        id="warning-parameters",
                                        size="sm",
                                        centered=True,
                                    ),
                                ],
                                className="page-with-side-bar",
                            ),
                        ],
                        className="vertical-page",
                    )
                ],
                id="parameters_layout",
                style={"display": "none"},
            ),
            # Model
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        className="progress-bar",
                                        children=[
                                            html.Div(
                                                className="progress-step",
                                                children=[
                                                    html.Div(className="step-circle"),
                                                    html.Div(
                                                        "Upload", className="step-label"
                                                    ),
                                                ],
                                            ),
                                            html.Div(className="progress-line"),
                                            html.Div(
                                                className="progress-step",
                                                children=[
                                                    html.Div(className="step-circle"),
                                                    html.Div(
                                                        "Data", className="step-label"
                                                    ),
                                                ],
                                            ),
                                            html.Div(className="progress-line"),
                                            html.Div(
                                                className="progress-step",
                                                children=[
                                                    html.Div(className="step-circle"),
                                                    html.Div(
                                                        "Parameters",
                                                        className="step-label",
                                                    ),
                                                ],
                                            ),
                                            html.Div(className="progress-line"),
                                            html.Div(
                                                className="progress-step",
                                                children=[
                                                    html.Div(
                                                        className="step-circle blue-circle"
                                                    ),
                                                    html.Div(
                                                        "Model", className="step-label"
                                                    ),
                                                ],
                                            ),
                                        ],
                                    )
                                ],
                                className="side-bar",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Div(
                                                "Here you can select which aggregation function you want to use in TOPSIS ranking",
                                                className="info",
                                            ),
                                            html.Div(
                                                "Additionally you can change the color scale for your plots",
                                                className="info",
                                            ),
                                        ],
                                        className="info-container",
                                    ),
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.Div(
                                                        "Choose aggregation function:"
                                                    ),
                                                    dcc.RadioItems(
                                                        [
                                                            {
                                                                "label": [
                                                                    html.Span(
                                                                        "R: Based on distance from the ideal and anti-ideal solution",
                                                                        className="css-radio-item",
                                                                    ),
                                                                    html.Div(
                                                                        html.Img(
                                                                            src="assets/plotR.png",
                                                                            id="plot-r-img",
                                                                        )
                                                                    ),
                                                                ],
                                                                "value": "R",
                                                            },
                                                            {
                                                                "label": [
                                                                    html.Span(
                                                                        "I: Based on distance from the ideal solution",
                                                                        className="css-radio-item",
                                                                    ),
                                                                    html.Div(
                                                                        html.Img(
                                                                            src="assets/plotI.png",
                                                                            id="plot-i-img",
                                                                        )
                                                                    ),
                                                                ],
                                                                "value": "I",
                                                            },
                                                            {
                                                                "label": [
                                                                    html.Span(
                                                                        "A: Based on distance from the anti-ideal solution",
                                                                        className="css-radio-item",
                                                                    ),
                                                                    html.Div(
                                                                        html.Img(
                                                                            src="assets/plotA.png",
                                                                            id="plot-a-img",
                                                                        )
                                                                    ),
                                                                ],
                                                                "value": "A",
                                                            },
                                                        ],
                                                        value="R",
                                                        id="wizard-model-input-radio-items",
                                                    ),
                                                ],
                                                className="css-radio-items",
                                            ),
                                            html.Div(
                                                [
                                                    html.Div(
                                                        "Choose color scale for plot:"
                                                    ),
                                                    dcc.Dropdown(
                                                        options=px.colors.named_colorscales(),
                                                        value="jet",
                                                        clearable=False,
                                                        id="wizard-model-input-dropdown-color",
                                                    ),
                                                    dcc.Graph(
                                                        id="color-preview-output"
                                                    ),
                                                ],
                                                className="css-radio-items",
                                            ),
                                        ],
                                        id="model-content",
                                    ),
                                    # https://dash.plotly.com/dash-core-components/radioitems
                                    html.Div(
                                        [
                                            html.Button(
                                                "Back",
                                                id="model-to-param",
                                                className="back-button",
                                            ),
                                            dcc.Link(
                                                html.Button(
                                                    "Finish", className="finish-button"
                                                ),
                                                href="/main_dash_layout",
                                            ),
                                        ],
                                        id="nav-buttons",
                                    ),
                                ],
                                className="page-with-side-bar",
                            ),
                        ],
                        className="vertical-page",
                    )
                ],
                id="model_layout",
                style={"display": "none"},
            ),
        ]
    )


@app.callback(
    Output("color-preview-output", "figure"),
    Input("wizard-model-input-dropdown-color", "value"),
)
def change_colorscale(scale):
    trace = go.Heatmap(z=np.linspace(0, 1, 1000).reshape(1, -1), showscale=False)

    layout = go.Layout(
        height=50,
        width=500,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        clickmode="none",
    )
    trace["colorscale"] = scale
    fig = {"data": [trace], "layout": layout}
    return fig


@app.callback(
    Output("model-to-param", "value"),
    Input("wizard-model-input-radio-items", "value"),
    Input("wizard-model-input-dropdown-color", "value"),
)
def get_agg_fn(agg, colour):
    global agg_g
    global colour_g
    colour_g = colour
    agg_g = agg
    return "Back"


@app.callback(
    [
        Output("data-preview", "children"),
        Output("data-table", "children", allow_duplicate=True),
        Output(
            "wizard-parameters-output-params-table", "children", allow_duplicate=True
        ),
        Output("data_upload_layout", "style", allow_duplicate=True),
        Output("data_layout", "style", allow_duplicate=True),
        Output("parameters_layout", "style", allow_duplicate=True),
        Output("model_layout", "style", allow_duplicate=True),
        Output("warning-upload-body", "children", allow_duplicate=True),
        Output("warning-upload", "is_open", allow_duplicate=True),
    ],
    [Input("wizard_data_input_submit-button", "n_clicks")],
    [
        State("wizard_state_stored-data", "data"),
        State("wizard_state_stored-params", "data"),
    ],
    prevent_initial_call=True,
)
def submit(n_clicks, data, params):

    param_keys = ["criterion", "weight", "expert-min", "expert-max", "objective"]
    warnings_children = html.Div([])
    is_open = False

    if n_clicks:
        data_preview = dash_table.DataTable(
            data=data,
            columns=[{"name": i, "id": i} for i in data[0].keys()],
            style_cell={"textAlign": "left"},
            page_size=8,
        )
        data_table = dcc.Store(id="wizard_state_stored-data", data=data)
        if (
            params is not None
            and check_parameters_wizard_data_files(data, params, param_keys) == -1
        ):
            # print('Prevent update - Wrong parameters format. Make sure that provided params file corresponds to uploaded data file.')
            warnings_children = html.Div(
                [
                    "Wrong parameters format. Make sure that provided params file corresponds to uploaded data file."
                ]
            )
            is_open = True
            return (
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                warnings_children,
                is_open,
            )

        columns = return_columns_wizard_parameters_params_table(param_keys)

        criteria = list(data[0].keys())
        df = pd.DataFrame.from_dict(data).set_index(criteria[0])

        weights, expert_mins, expert_maxs, objectives = (
            fill_parameters_wizard_parameters_params(params, df, param_keys)
        )

        data_params = []

        for id, c in enumerate(criteria[1:]):
            data_params.append(
                dict(
                    criterion=c,
                    **{
                        param_keys[1]: weights[id],
                        param_keys[2]: expert_mins[id],
                        param_keys[3]: expert_maxs[id],
                        param_keys[4]: objectives[id],
                    },
                )
            )

        if not data_params:
            warnings_children = html.Div(
                [
                    "Wrong data format. Make sure that proper decimal and delimiter separators are set. Data showed in the preview should have a form of a table."
                ]
            )
            is_open = True
            # print('Prevent update - Wrong data format. Make sure that proper decimal and delimiter separators are set. Data showed in the preview should have a form of a table.')
            return (
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                warnings_children,
                is_open,
            )

        params_table = html.Div(
            [
                # https://dash.plotly.com/datatable/editable
                # https://community.plotly.com/t/resolved-dropdown-options-in-datatable-not-showing/20366
                dash_table.DataTable(
                    id="wizard-parameters-input-parameters-table",
                    columns=columns,
                    style_cell={"textAlign": "left"},
                    data=data_params,
                    editable=True,
                    dropdown={
                        param_keys[4]: {
                            "options": [
                                {"label": i, "value": i} for i in ["min", "max"]
                            ],
                            "clearable": False,
                        },
                    },
                ),
                html.Div("Set all to Min/Max"),
                dcc.Dropdown(
                    ["-", "min", "max"],
                    "-",
                    id="wizard-parameters-input-objectives-dropdown",
                    clearable=False,
                ),
            ],
            className="params-content",
        )
        return (
            data_preview,
            data_table,
            params_table,
            {"display": "none"},
            {"display": "block"},
            {"display": "none"},
            {"display": "none"},
            warnings_children,
            is_open,
        )
    else:
        return (
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            warnings_children,
            is_open,
        )


@app.callback(
    [
        Output("data_upload_layout", "style", allow_duplicate=True),
        Output("data_layout", "style", allow_duplicate=True),
        Output("parameters_layout", "style", allow_duplicate=True),
        Output("model_layout", "style", allow_duplicate=True),
    ],
    [Input("data-to-param", "n_clicks")],
    prevent_initial_call=True,
)
def button_data_params(n_clicks):
    if n_clicks:
        return (
            {"display": "none"},
            {"display": "none"},
            {"display": "block"},
            {"display": "none"},
        )
    else:
        return no_update, no_update, no_update, no_update


@app.callback(
    [
        Output("data_upload_layout", "style", allow_duplicate=True),
        Output("data_layout", "style", allow_duplicate=True),
        Output("parameters_layout", "style", allow_duplicate=True),
        Output("model_layout", "style", allow_duplicate=True),
    ],
    [Input("param-to-data", "n_clicks")],
    prevent_initial_call=True,
)
def button_params_data(n_clicks):
    if n_clicks:
        return (
            {"display": "none"},
            {"display": "block"},
            {"display": "none"},
            {"display": "none"},
        )
    else:
        return no_update, no_update, no_update, no_update


@app.callback(
    [
        Output("data_upload_layout", "style", allow_duplicate=True),
        Output("data_layout", "style", allow_duplicate=True),
        Output("parameters_layout", "style", allow_duplicate=True),
        Output("model_layout", "style", allow_duplicate=True),
    ],
    [Input("param-to-model", "n_clicks")],
    prevent_initial_call=True,
)
def button_params_model(n_clicks):
    if n_clicks:
        return (
            {"display": "none"},
            {"display": "none"},
            {"display": "none"},
            {"display": "block"},
        )
    else:
        return no_update, no_update, no_update, no_update


@app.callback(
    [
        Output("data_upload_layout", "style", allow_duplicate=True),
        Output("data_layout", "style", allow_duplicate=True),
        Output("parameters_layout", "style", allow_duplicate=True),
        Output("model_layout", "style", allow_duplicate=True),
    ],
    [Input("model-to-param", "n_clicks")],
    prevent_initial_call=True,
)
def button_model_params(n_clicks):
    if n_clicks:
        return (
            {"display": "none"},
            {"display": "none"},
            {"display": "block"},
            {"display": "none"},
        )
    else:
        return no_update, no_update, no_update, no_update


def check_title_wizard_data_title(text):

    for c in text:
        if c.isalnum():
            continue
        if c == " " or c == "_" or c == "-":
            continue
        return False

    return True


@app.callback(
    Output(
        "wizard-data-after-submit-output-project-title",
        "children",
        allow_duplicate=True,
    ),
    Input("wizard-data-input-title", "n_clicks"),
    State("wizard-data-input-title", "children"),
    prevent_initial_call=True,
)
def edit_title_wizard_data_after_submit(click, text):

    if click:
        return html.Div(
            [
                dcc.Input(
                    id="wizard-data-input-type-title",
                    type="text",
                    placeholder=text,
                    minLength=1,
                    maxLength=20,
                ),
            ]
        )

    return no_update


@app.callback(
    Output(
        "wizard-data-after-submit-output-project-title",
        "children",
        allow_duplicate=True,
    ),
    Input("css-edit-icon", "n_clicks"),
    State("wizard-data-input-title", "children"),
    prevent_initial_call=True,
)
def toggle_edit_mode(click, text):
    if click:
        return html.Div(
            [
                dcc.Input(
                    id="wizard-data-input-type-title",
                    type="text",
                    placeholder=text,
                    minLength=1,
                    maxLength=20,
                ),
            ]
        )

    return no_update


@app.callback(
    Output("wizard-data-after-submit-output-project-title", "children"),
    Output("warning-data-body", "children"),
    Output("warning-data", "is_open"),
    Input("wizard-data-input-type-title", "n_submit"),
    State("wizard-data-input-type-title", "value"),
)
def edit_title_wizard_data_after_submit(enter, text):

    warnings_children = html.Div([])
    is_open = False
    if enter and text:
        if check_title_wizard_data_title(text):
            global title
            title = text
            return (
                html.Div([html.Div(text, id="wizard-data-input-title")]),
                warnings_children,
                is_open,
            )
        else:
            # print("Prevent update - Allowed characters in title are only english letters, digits and white space (' '), dash ('-') or underscore ('_').")
            warnings_children = html.Div(
                [
                    "Allowed characters in title are only english letters, digits and white space (' '), dash ('-') or underscore ('_')."
                ]
            )
            is_open = True

    return no_update, warnings_children, is_open


def check_updated_params_wizard_parameters(df_data, df_params, param_keys):
    warnings = []

    warning = {"text": "", "value": "", "column": "", "row_id": -1}
    df_criteria = df_data.drop(columns=df_data.columns[0], axis=1, inplace=False)
    criteria = df_criteria.columns.values.tolist()

    # weights
    if (df_params[param_keys[1]] < 0).any():

        for id, val in enumerate(df_params[param_keys[1]]):
            if val < 0:
                warning["text"] = "Weight must be a non-negative number.\n"
                warning["value"] = val
                warning["column"] = param_keys[1]
                warning["row_id"] = criteria[id]

                warnings.append(warning)

    if df_params[param_keys[1]].sum() == 0:
        warning["text"] = "At least one weight must be greater than 0.\n"
        warning["value"] = 0
        warning["column"] = param_keys[1]
        warning["row_id"] = "each"

        warnings.append(warning)

    # expert range
    lower_bound = df_data.min()
    upper_bound = df_data.max()

    for id, (lower, upper, mini, maxi) in enumerate(
        zip(
            lower_bound[1:],
            upper_bound[1:],
            df_params[param_keys[2]],
            df_params[param_keys[3]],
        )
    ):
        if mini > maxi:
            warning["text"] = (
                "Min value must be lower or equal than max value (" + str(mini) + ").\n"
            )
            warning["value"] = mini
            warning["column"] = param_keys[2]
            warning["row_id"] = criteria[id]
            warnings.append(warning)

        if lower < mini:
            warning["text"] = (
                "Min value must be lower or equal than the minimal value of given criterion ("
                + str(lower)
                + ").\n"
            )
            warning["value"] = mini
            warning["column"] = param_keys[2]
            warning["row_id"] = criteria[id]
            warnings.append(warning)

        if upper > maxi:
            warning["text"] = (
                "Max value must be greater or equal than the maximal value of given criterion ("
                + str(upper)
                + ").\n"
            )
            warning["value"] = maxi
            warning["column"] = param_keys[2]
            warning["row_id"] = criteria[id]
            warnings.append(warning)

    # return list(set(warnings))
    return warnings


def parse_warning(warning):

    warning2 = (
        warning["text"]
        + "\n"
        + "You entered "
        + "'"
        + str(warning["value"])
        + "'"
        + " in "
        + "'"
        + str(warning["column"])
        + "' column"
        + " in "
        + "'"
        + str(warning["row_id"])
        + "' row"
        + ".\n"
        + "Changes were not applied."
    )

    return warning2


# Approach 2 - iterate through whole table
@app.callback(
    Output("wizard-parameters-output-params-table", "children"),
    Output("warning-parameters-body", "children"),
    Output("warning-parameters", "is_open"),
    Input("wizard-parameters-input-parameters-table", "data_timestamp"),
    Input("wizard-parameters-input-objectives-dropdown", "value"),
    State("wizard_state_stored-data", "data"),
    State("wizard-parameters-input-parameters-table", "data"),
    State("wizard-parameters-input-parameters-table", "data_previous"),
)
def update_table_wizard_parameters(
    timestamp, objectives_val, data, params, params_previous
):
    # https://community.plotly.com/t/detecting-changed-cell-in-editable-datatable/26219/3
    # https://dash.plotly.com/duplicate-callback-outputs

    param_keys = ["criterion", "weight", "expert-min", "expert-max", "objective"]
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
        df_params_prev = pd.DataFrame.from_dict(params_previous).set_index(
            criteria_params[0]
        )

        if not df_params[param_keys[4]].equals(df_params_prev[param_keys[4]]):
            objectives_val = "-"

    if objectives_val != "-":
        for id, val in enumerate(params):
            params[id][param_keys[4]] = objectives_val

    global params_g
    params_g = params

    # switches = [return_toggle_switch(id, o) for id, o in enumerate(df_params['objective'])]

    return (
        html.Div(
            [
                # https://dash.plotly.com/datatable/editable
                # https://community.plotly.com/t/resolved-dropdown-options-in-datatable-not-showing/20366
                dcc.Store(id="wizard_state_stored-data", data=data),
                dash_table.DataTable(
                    id="wizard-parameters-input-parameters-table",
                    columns=columns,
                    style_cell={"textAlign": "left"},
                    data=params,
                    editable=True,
                    dropdown={
                        param_keys[4]: {
                            "options": [
                                {"label": i, "value": i} for i in ["min", "max"]
                            ],
                            "clearable": False,
                        },
                    },
                ),
                html.Div("Set all to Min/Max"),
                dcc.Dropdown(
                    ["-", "min", "max"],
                    objectives_val,
                    id="wizard-parameters-input-objectives-dropdown",
                    clearable=False,
                ),
            ]
        ),
        warnings_children,
        is_open,
    )


@app.callback(
    Output("wizard-model-output-view", "children"),
    Input("wizard-model-input-radio-items", "value"),
)
def show_view_wizard_model(agg):
    if agg == "R":
        return html.Div(
            style={"height": "50px", "width": "50px", "background-color": "#FF0000"},
            id="wizard-model-output-view",
        )
    if agg == "I":
        return html.Div(
            style={"height": "50px", "width": "50px", "background-color": "#00FF00"},
            id="wizard-model-output-view",
        )
    if agg == "A":
        return html.Div(
            style={"height": "50px", "width": "50px", "background-color": "#0000FF"},
            id="wizard-model-output-view",
        )


# ==============================================================
#   PLAYGROUND
# ==============================================================


def main_dash_layout2():
    global data
    data = pd.read_csv("data/bus.csv", sep=";")
    f = open("data/bus_params.json")
    params = json.load(f)
    params = pd.DataFrame.from_dict(params)
    params = params.to_dict("records")
    global params_g
    params_g = params
    global agg_g
    agg_g = "R"
    global colour_g
    colour_g = "jet"
    return main_dash_layout()


def main_dash_layout():
    global proceed
    proceed = True
    global data
    data = data.set_index(data.columns[0])
    if agg_g == "R":
        buses = wmsdt.WMSDTransformer(wmsdt.RTOPSIS, args.solver)
    elif agg_g == "A":
        buses = wmsdt.WMSDTransformer(wmsdt.ATOPSIS, args.solver)
    else:
        buses = wmsdt.WMSDTransformer(wmsdt.ITOPSIS, args.solver)

    criteria_params = list(params_g[0].keys())
    params = pd.DataFrame.from_dict(params_g).set_index(criteria_params[0])
    buses.fit_transform(
        data, params["weight"].to_list(), params["objective"].to_list(), None
    )
    global buses_g
    buses_g = buses
    return html.Div(
        children=[
            html.Div(id="wizard-data"),
            dcc.Tabs(
                children=[
                    dcc.Tab(
                        label="Ranking visualization",
                        children=[
                            html.Div(
                                [
                                    html.Div(
                                        "Here is shown your normalized dataset and dataset visualization in WMSD",
                                        className="info",
                                    )
                                ],
                                className="info-container",
                            ),
                            ranking_vizualization(buses),
                        ],
                    ),
                    dcc.Tab(
                        label="Improvement actions",
                        children=[
                            html.Div(
                                [
                                    html.Div(
                                        "You can use selector of methods to check necessary improvement in chosen alternative to overrank other alternative, and then download a report",
                                        className="info",
                                    )
                                ],
                                className="info-container",
                            ),
                            improvement_actions(buses),
                        ],
                    ),
                    dcc.Tab(
                        label="Analysis of parameters",
                        children=[
                            html.Div(
                                [
                                    html.Div(
                                        "Here you can analyze and download previously set parameters",
                                        className="info",
                                    )
                                ],
                                className="info-container",
                            ),
                            model_setter(),
                        ],
                    ),
                ]
            ),
            dbc.Modal(
                [dbc.ModalHeader("Warning"), dbc.ModalBody(id="warning-main1-body")],
                id="warning-main1",
                size="sm",
                centered=True,
            ),
            dbc.Modal(
                [dbc.ModalHeader("Warning"), dbc.ModalBody(id="warning-main2-body")],
                id="warning-main2",
                size="sm",
                centered=True,
            ),
            dbc.Modal(
                [dbc.ModalHeader("Warning"), dbc.ModalBody(id="warning-main3-body")],
                id="warning-main3",
                size="sm",
                centered=True,
            ),
            dbc.Modal(
                [dbc.ModalHeader("Warning"), dbc.ModalBody(id="warning-main4-body")],
                id="warning-main4",
                size="sm",
                centered=True,
            ),
            dbc.Modal(
                [dbc.ModalHeader("Warning"), dbc.ModalBody(id="warning-main5-body")],
                id="warning-main5",
                size="sm",
                centered=True,
            ),
        ]
    )


def model_setter():
    return html.Div(id="param-table", children=None)


@app.callback(
    Output("param-table", "children"),
    Input("param-table", "value"),
    prevent_initial_call=False,
)
def display_parameters(a):
    global params_g
    params = params_g

    params_labels = ["criterion", "weight", "expert-min", "expert-max", "objective"]
    columns = return_columns_wizard_parameters_params_table(params_labels)
    df = pd.DataFrame.from_dict(params)

    return html.Div(
        id="aop-tab",
        className="tab",
        children=[
            dash_table.DataTable(
                df.to_dict("records"),
                [{"name": i, "id": i} for i in df.columns],
                style_cell={"textAlign": "left"},
            ),
            html.Button("Download", id="json-download-button"),
            dcc.Download(id="json-download"),
        ],
    )


@app.callback(
    Output("json-download", "data"),
    Input("json-download-button", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    df = pd.DataFrame.from_dict(params_g)
    return dcc.send_data_frame(df.to_json, "params.json")


def formating(f):
    return f"{f:.2f}"


def ranking_vizualization(buses):
    df = buses.X_new.sort_values(agg_g, ascending=False) * np.append(
        buses_g.weights, [1, 1, 1]
    )
    # df = buses.X_new.applymap(formating)
    df = df.applymap(formating)

    df = df.assign(Rank=None)
    columns = df.columns.tolist()
    columns = columns[-1:] + columns[:-1]
    df = df[columns]

    alternative_names = df.index.tolist()
    for alternative in alternative_names:
        df["Rank"][alternative] = buses._ranked_alternatives.index(alternative) + 1

    df.index.rename("Name", inplace=True)
    df.reset_index(inplace=True)
    fig = buses.plot(plot_name=title, color=colour_g)
    fig.update_layout(clickmode="event+select")
    return html.Div(
        id="rv-tab",
        className="tab",
        children=[
            dcc.Graph(id="vizualization", figure=fig),
            dash_table.DataTable(
                df.to_dict("records"),
                [{"name": i, "id": i} for i in df.columns],
                style_cell={"textAlign": "right"},
                sort_action="native",
                id="datatable",
                style_table={"overflowX": "auto"},
            ),
            html.Div(id="selected-data"),
        ],
    )


"""
@app.callback(
    Output('selected-data', 'children'),
    Input('vizualization', 'selectedData'))
def display_selected_data(selectedData):
    print(selectedData)
    return json.dumps(selectedData, indent=2)
"""
"""
@app.callback(
    Output('selected-data', 'children'),
    Input('vizualization', 'clickData'))
def display_click_data(clickData):
    print(clickData)
    return json.dumps(clickData, indent=2)
"""


def improvement_actions(buses):
    global buses_g
    buses_g = buses
    global raport_viz
    raport_viz = "hidden"
    ids = buses_g.X_new.index
    return html.Div(
        id="ia-tab",
        className="tab",
        children=[
            dbc.Container(
                [
                    html.Div(id="viz", children=ranking_vizualization(buses)),
                    html.Div(
                        [
                            html.Div(
                                id="ia-options",
                                children=[
                                    html.Div(
                                        children=[
                                            "Improvement action:",
                                            dcc.Dropdown(
                                                id="choose-method",
                                                options=[
                                                    {"label": method, "value": method}
                                                    for method in [
                                                        "improvement_mean",
                                                        "improvement_std",
                                                        "improvement_features",
                                                        "improvement_genetic",
                                                        "improvement_single_feature",
                                                    ]
                                                ],
                                                value="improvement_mean",
                                                clearable=False,
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        children=[
                                            "Alternative to improve:",
                                            dcc.Dropdown(
                                                id="alternative-to-improve", options=ids
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        [
                                            html.Div(
                                                children=[
                                                    "Alternative to overcome:",
                                                    dcc.Dropdown(
                                                        id="alternative-to-overcame",
                                                        options=ids,
                                                    ),
                                                ],
                                                id="con-alternative-to-overcame",
                                            ),
                                            html.Div(["OR"]),
                                            html.Div(
                                                children=[
                                                    "Rank to achieve:",
                                                    dcc.Input(
                                                        type="number",
                                                        id="rank-to-achive",
                                                    ),
                                                ],
                                                id="con-rank-to-achive",
                                            ),
                                        ],
                                        id="css-alt-or-rank",
                                    ),
                                    html.Div(id="conditional-settings"),
                                    html.Button(
                                        "Advanced settings",
                                        id="advanced-settings",
                                        n_clicks=0,
                                    ),
                                    html.Div(id="advanced-content", children=None),
                                    html.Button("Apply", id="apply-button", n_clicks=0),
                                    html.Div(id="improvement-result", children=None),
                                    html.Button(
                                        "Download report",
                                        id="download-raport",
                                        n_clicks=0,
                                        style={
                                            "visibility": raport_viz,
                                        },
                                    ),
                                    html.Div(id="download-placeholder"),
                                ],
                            )
                        ],
                        id="ia-options-content",
                    ),
                ],
                id="ia-tab-content",
            )
        ],
    )


@app.callback(
    Output("alternative-to-overcame", "value"),
    Input("rank-to-achive", "value"),
    prevent_initial_call=True,
)
def update_alternative(rank):
    if rank is not None:
        return buses_g._ranked_alternatives[rank - 1]


@app.callback(
    Output("rank-to-achive", "value"),
    Input("alternative-to-overcame", "value"),
    prevent_initial_call=True,
)
def update_rank(alternative_to_overcame):
    if alternative_to_overcame is not None:
        ranking = buses_g._ranked_alternatives
        for i in range(len(ranking)):
            if ranking[i] == alternative_to_overcame:
                return i + 1


@app.callback(
    Output("download-raport", "n_clicks"), Input("download-raport", "n_clicks")
)
def report_generation(n):
    if n == 1:
        write_raport()
        return 0
    else:
        return 0


@app.callback(Output("improvement-result", "children"), Input("choose-method", "value"))
def improvement_result_setup(value):
    name = value + "-result"
    return html.Div(id=name)


@app.callback(
    Output("conditional-settings", "children"), Input("choose-method", "value")
)
def set_conditional_settings(value):
    features = list(buses_g.X_new.columns[:-3])
    print(features)
    if value == "improvement_features":
        return html.Div(
            children=[
                html.Div(
                    [
                        html.Div("Features to change:"),
                        html.Div(
                            html.I(className="fa-solid fa-question fa-xs"),
                            id="features-help",
                        ),
                        dbc.Tooltip(
                            "Features that you allow to change",
                            target="features-help",
                        ),
                    ],
                    className="css-help",
                ),
                dcc.Dropdown(
                    id="features-to-change", options=features + ["all"], multi=True
                ),
            ]
        )
    elif value == "improvement_genetic":
        return html.Div(
            children=[
                html.Div(
                    [
                        html.Div("Features to change:"),
                        html.Div(
                            html.I(className="fa-solid fa-question fa-xs"),
                            id="features-genetic-help",
                        ),
                        dbc.Tooltip(
                            "Features that you allow to change",
                            target="features-genetic-help",
                        ),
                    ],
                    className="css-help",
                ),
                dcc.Dropdown(
                    id="features-to-change", options=features + ["all"], multi=True
                ),
            ]
        )
    elif value == "improvement_single_feature":
        return html.Div(
            children=[
                html.Div(
                    [
                        html.Div("Feature to change:"),
                        html.Div(
                            html.I(className="fa-solid fa-question fa-xs"),
                            id="feature-help",
                        ),
                        dbc.Tooltip(
                            "One feature that you allow to change",
                            target="feature-help",
                        ),
                    ],
                    className="css-help",
                ),
                dcc.Dropdown(id="feature-to-change", options=features),
            ]
        )


@app.callback(
    Output("features-to-change", "value"), Input("features-to-change", "value")
)
def all_values(value):
    if value is not None and "all" in value:
        return list(buses_g.X_new.columns[:-3])
    else:
        return value


@app.callback(
    Output("advanced-content", "children"),
    Input("choose-method", "value"),
    Input("advanced-settings", "n_clicks"),
    prevent_initial_call=False,
)
def set_advanced_settings(value, n_clicks):
    if n_clicks % 2 == 0:
        is_hidden = "hidden"
    else:
        is_hidden = "visible"
    if value == "improvement_mean":
        return html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(
                            [
                                html.Div("Epsilon:"),
                                html.Div(
                                    html.I(className="fa-solid fa-question fa-xs"),
                                    id="epsilon-help",
                                ),
                                dbc.Tooltip(
                                    "Maximum value allowed to be better than desired alternative",
                                    target="epsilon-help",
                                ),
                            ],
                            className="css-help",
                        ),
                        dcc.Input(type="number", id="epsilon", value=0.000001),
                    ]
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div("Allow std:"),
                                html.Div(
                                    html.I(className="fa-solid fa-question fa-xs"),
                                    id="allow-std-help",
                                ),
                                dbc.Tooltip(
                                    "True if you allow change in std, False otherwise",
                                    target="allow-std-help",
                                ),
                            ],
                            className="css-help",
                        ),
                        dcc.Input(type="text", id="allow-std", value="False"),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(
                            [
                                html.Div("Number of solutions:"),
                                html.Div(
                                    html.I(className="fa-solid fa-question fa-xs"),
                                    id="solutions-number-help",
                                ),
                                dbc.Tooltip(
                                    "Number of shown solutions fitting the improvement",
                                    target="solutions-number-help",
                                ),
                            ],
                            className="css-help",
                        ),
                        dcc.Input(type="number", id="solutions-number", value=5),
                    ]
                ),
            ],
            style={
                "visibility": is_hidden,
            },
        )
    elif value == "improvement_features":
        return html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(
                            [
                                html.Div("Epsilon:"),
                                html.Div(
                                    html.I(className="fa-solid fa-question fa-xs"),
                                    id="epsilon2-help",
                                ),
                                dbc.Tooltip(
                                    "Maximum value allowed to be better than desired alternative",
                                    target="epsilon2-help",
                                ),
                            ],
                            className="css-help",
                        ),
                        dcc.Input(type="number", id="epsilon", value=0.000001),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(
                            [
                                html.Div("Boundary values:"),
                                html.Div(
                                    html.I(className="fa-solid fa-question fa-xs"),
                                    id="boundary-values-help",
                                ),
                                dbc.Tooltip(
                                    "Maximum values of chosen features to be achieved, equal amount as features to change",
                                    target="boundary-values-help",
                                ),
                            ],
                            className="css-help",
                        ),
                        dcc.Input(type="text", id="boundary-values"),
                    ]
                ),
            ],
            style={
                "visibility": is_hidden,
            },
        )
    elif value == "improvement_genetic":
        return html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(
                            [
                                html.Div("Epsilon:"),
                                html.Div(
                                    html.I(className="fa-solid fa-question fa-xs"),
                                    id="epsilon3-help",
                                ),
                                dbc.Tooltip(
                                    "Maximum value allowed to be better than desired alternative",
                                    target="epsilon3-help",
                                ),
                            ],
                            className="css-help",
                        ),
                        dcc.Input(type="number", id="epsilon", value=0.000001),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(
                            [
                                html.Div("Boundary values:"),
                                html.Div(
                                    html.I(className="fa-solid fa-question fa-xs"),
                                    id="boundary-values2-help",
                                ),
                                dbc.Tooltip(
                                    "Maximum values of chosen features to be achieved, equal amount as features to change",
                                    target="boundary-values2-help",
                                ),
                            ],
                            className="css-help",
                        ),
                        dcc.Input(type="text", id="boundary-values"),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(
                            [
                                html.Div("Allow deterioration:"),
                                html.Div(
                                    html.I(className="fa-solid fa-question fa-xs"),
                                    id="allow-det-help",
                                ),
                                dbc.Tooltip(
                                    "True if you allow deterioration, False otherwise",
                                    target="allow-det-help",
                                ),
                            ],
                            className="css-help",
                        ),
                        dcc.Input(type="text", id="allow-deterioration", value="False"),
                    ]
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div("Popsize:"),
                                html.Div(
                                    html.I(className="fa-solid fa-question fa-xs"),
                                    id="popsize-help",
                                ),
                                dbc.Tooltip(
                                    "Population size for genetic algorithm",
                                    target="popsize-help",
                                ),
                            ],
                            className="css-help",
                        ),
                        dcc.Input(type="number", id="popsize"),
                    ]
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div("Generations:"),
                                html.Div(
                                    html.I(className="fa-solid fa-question fa-xs"),
                                    id="generations-help",
                                ),
                                dbc.Tooltip(
                                    "Number of generations in genetic algorithm",
                                    target="generations-help",
                                ),
                            ],
                            className="css-help",
                        ),
                        dcc.Input(type="number", id="generations", value=200),
                    ]
                ),
            ],
            style={
                "visibility": is_hidden,
            },
        )
    elif value == "improvement_single_feature":
        return html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(
                            [
                                html.Div("Epsilon:"),
                                html.Div(
                                    html.I(className="fa-solid fa-question fa-xs"),
                                    id="epsilon4-help",
                                ),
                                dbc.Tooltip(
                                    "Maximum value allowed to be better than desired alternative",
                                    target="epsilon4-help",
                                ),
                            ],
                            className="css-help",
                        ),
                        dcc.Input(type="number", id="epsilon", value=0.000001),
                    ]
                )
            ],
            style={
                "visibility": is_hidden,
            },
        )
    elif value == "improvement_std":
        return html.Div(
            children=[
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div("Epsilon:"),
                                html.Div(
                                    html.I(className="fa-solid fa-question fa-xs"),
                                    id="epsilon5-help",
                                ),
                                dbc.Tooltip(
                                    "Maximum value allowed to be better than desired alternative",
                                    target="epsilon5-help",
                                ),
                            ],
                            className="css-help",
                        ),
                        dcc.Input(type="number", id="epsilon", value=0.000001),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(
                            [
                                html.Div("Number of solutions:"),
                                html.Div(
                                    html.I(className="fa-solid fa-question fa-xs"),
                                    id="solutions-number2-help",
                                ),
                                dbc.Tooltip(
                                    "Number of shown solutions fitting the improvement",
                                    target="solutions-number2-help",
                                ),
                            ],
                            className="css-help",
                        ),
                        dcc.Input(type="number", id="solutions-number", value=5),
                    ]
                ),
            ],
            style={
                "visibility": is_hidden,
            },
        )


@app.callback(
    Output("improvement_genetic-result", "children"),
    Output("warning-main1-body", "children"),
    Output("warning-main1", "is_open"),
    [Input("apply-button", "n_clicks")],
    # Input('alternative-to-improve', 'value'),
    # Input('alternative-to-overcame', 'value'),
    State("alternative-to-improve", "value"),
    State("alternative-to-overcame", "value"),
    State("epsilon", "value"),
    State("features-to-change", "value"),
    State("boundary-values", "value"),
    State("allow-deterioration", "value"),
    State("popsize", "value"),
    State("generations", "value"),
    State("choose-method", "value"),
    prevent_initial_call=True,
)
def improvement_genetic_results(
    n,
    alternative_to_improve,
    alternative_to_overcame,
    epsilon,
    features_to_change,
    boundary_values,
    allow_deterioration,
    popsize,
    generations,
    method,
):
    global proceed
    proceed = False
    global improvement
    warnings_children = html.Div([])
    is_open = False

    if (
        alternative_to_improve is None
        or alternative_to_overcame is None
        or features_to_change is None
    ):
        # print("Warning Fields: alternative_to_improve, alternative_to_overcome and features_to_change need to be filed")
        warnings_children = html.Div(
            [
                "Alternative_to_improve, alternative_to_overcome and features_to_change need to be filed"
            ]
        )
        is_open = True
        proceed = True
        improvement = None
        return None, warnings_children, is_open

    if n > 0:
        if boundary_values is not None:
            boundary_values = boundary_values.split(",")
            boundary_values = [float(x) for x in boundary_values]

        if epsilon is None:
            epsilon = 0.000001

        if allow_deterioration is None:
            allow_deterioration = False
        else:
            allow_deterioration = bool(allow_deterioration)

        if generations is None:
            generations = 200

        no_exception = True

        try:
            improvement = buses_g.improvement(
                method,
                alternative_to_improve,
                alternative_to_overcame,
                epsilon,
                features_to_change=features_to_change,
                boundary_values=boundary_values,
                allow_deterioration=allow_deterioration,
                popsize=popsize,
                n_generations=generations,
            )[:10]
        except Exception as e:
            print(e)
            no_exception = False

        # rounded_improvement = improvement.apply(formating)
        # rounded_improvement = [row.applymap(formating) for index, row in improvement.iterrows()]

        if no_exception:

            if improvement is None:
                proceed = True
                improvement = None
                # print("Warning no solution found")
                warnings_children = html.Div(["No solution found"])
                is_open = True
                # raise PreventUpdate
                return None, warnings_children, is_open

            rounded_improvement = improvement.apply(np.vectorize(formating))
            global improvement_parameters
            improvement_parameters = {
                "parameters": [
                    "method",
                    "alternative_to_improve",
                    "alternative_to_overcame",
                    "epsilon",
                    "features_to_change",
                    "boundary_values",
                    "allow_deterioration",
                    "popsize",
                    "generations",
                ],
                "values": [
                    method,
                    alternative_to_improve,
                    alternative_to_overcame,
                    epsilon,
                    features_to_change,
                    boundary_values,
                    allow_deterioration,
                    popsize,
                    generations,
                ],
            }
            global raport_viz
            raport_viz = "visible"
            proceed = True
            return (
                dash_table.DataTable(
                    rounded_improvement.to_dict("records"),
                    [{"name": i, "id": i} for i in rounded_improvement.columns],
                    style_cell={"textAlign": "left"},
                    style_table={"overflowX": "auto"},
                ),
                warnings_children,
                is_open,
            )

    proceed = True
    improvement = None
    raise PreventUpdate


@app.callback(Output("download-raport", "style"), Input("apply-button", "n_clicks"))
def raport_button_visibility(n):
    time.sleep(0.5)
    while True:
        if proceed:
            break
        time.sleep(0.5)
    return {"visibility": raport_viz}


@app.callback(
    Output("improvement_features-result", "children"),
    Output("warning-main2-body", "children"),
    Output("warning-main2", "is_open"),
    [Input("apply-button", "n_clicks")],
    # Input('alternative-to-improve', 'value'),
    # Input('alternative-to-overcame', 'value'),
    State("alternative-to-improve", "value"),
    State("alternative-to-overcame", "value"),
    State("epsilon", "value"),
    State("features-to-change", "value"),
    State("boundary-values", "value"),
    State("choose-method", "value"),
    prevent_initial_call=True,
)
def improvement_features_results(
    n,
    alternative_to_improve,
    alternative_to_overcame,
    epsilon,
    features_to_change,
    boundary_values,
    method,
):
    global proceed
    proceed = False
    global improvement
    warnings_children = html.Div([])
    is_open = False

    if (
        alternative_to_improve is None
        or alternative_to_overcame is None
        or features_to_change is None
    ):
        # print("Warning Fields: alternative_to_improve, alternative_to_overcome and features_to_change need to be filed")
        warnings_children = html.Div(
            [
                "Alternative_to_improve, alternative_to_overcome and features_to_change need to be filed"
            ]
        )
        is_open = True
        proceed = True
        improvement = None
        return None, warnings_children, is_open

    if boundary_values is not None:
        boundary_values = boundary_values.split(",")
        boundary_values = [float(x) for x in boundary_values]

    if n > 0:
        if epsilon is None:
            epsilon = 0.000001

        no_exception = True

        try:
            improvement = buses_g.improvement(
                method,
                alternative_to_improve,
                alternative_to_overcame,
                epsilon,
                features_to_change=features_to_change,
                boundary_values=boundary_values,
            )
        except Exception as e:
            print(e)
            no_exception = False

        if no_exception:

            if improvement is None:
                proceed = True
                improvement = None
                # print("Warning no solution found")
                # raise PreventUpdate
                warnings_children = html.Div(["No solution found"])
                is_open = True
                return None, warnings_children, is_open

            rounded_improvement = improvement.applymap(formating)
            global raport_viz
            raport_viz = "visible"
            proceed = True
            return (
                dash_table.DataTable(
                    rounded_improvement.to_dict("records"),
                    [{"name": i, "id": i} for i in rounded_improvement.columns],
                    style_cell={"textAlign": "left"},
                    style_table={"overflowX": "auto"},
                ),
                warnings_children,
                is_open,
            )

    proceed = True
    improvement = None
    raise PreventUpdate


@app.callback(
    Output("improvement_single_feature-result", "children"),
    Output("warning-main3-body", "children"),
    Output("warning-main3", "is_open"),
    [Input("apply-button", "n_clicks")],
    # Input('alternative-to-improve', 'value'),
    # Input('alternative-to-overcame', 'value'),
    State("alternative-to-improve", "value"),
    State("alternative-to-overcame", "value"),
    State("epsilon", "value"),
    State("feature-to-change", "value"),
    State("choose-method", "value"),
    prevent_initial_call=True,
)
def improvement_feature_results(
    n,
    alternative_to_improve,
    alternative_to_overcame,
    epsilon,
    feature_to_change,
    method,
):
    global proceed
    proceed = False
    global improvement
    warnings_children = html.Div([])
    is_open = False

    if (
        alternative_to_improve is None
        or alternative_to_overcame is None
        or feature_to_change is None
    ):
        # print("Warning Fields: alternative_to_improve, alternative_to_overcome and feature_to_change need to be filed")
        warnings_children = html.Div(
            [
                "Alternative_to_improve, alternative_to_overcome and features_to_change need to be filed"
            ]
        )
        is_open = True
        proceed = True
        improvement = None
        return None, warnings_children, is_open

    if n > 0:

        if epsilon is None:
            epsilon = 0.000001

        no_exception = True

        try:
            improvement = buses_g.improvement(
                method,
                alternative_to_improve,
                alternative_to_overcame,
                epsilon,
                feature_to_change=feature_to_change,
            )
        except Exception as e:
            print(e)
            no_exception = False

        if no_exception:

            if improvement is None:
                proceed = True
                improvement = None
                # print("Warning no solution found")
                # raise PreventUpdate
                warnings_children = html.Div(["No solution found"])
                is_open = True
                return None, warnings_children, is_open

            rounded_improvement = improvement.applymap(formating)
            global raport_viz
            raport_viz = "visible"
            proceed = True
            return (
                dash_table.DataTable(
                    rounded_improvement.to_dict("records"),
                    [{"name": i, "id": i} for i in rounded_improvement.columns],
                    style_cell={"textAlign": "left"},
                    style_table={"overflowX": "auto"},
                ),
                warnings_children,
                is_open,
            )

    proceed = True
    improvement = None
    raise PreventUpdate


@app.callback(
    Output("improvement_mean-result", "children"),
    Output("warning-main4-body", "children"),
    Output("warning-main4", "is_open"),
    [Input("apply-button", "n_clicks")],
    # Input('alternative-to-improve', 'value'),
    # Input('alternative-to-overcame', 'value'),
    State("alternative-to-improve", "value"),
    State("alternative-to-overcame", "value"),
    State("epsilon", "value"),
    State("allow-std", "value"),
    State("choose-method", "value"),
    State("solutions-number", "value"),
    prevent_initial_call=True,
)
def improvement_mean_results(
    n,
    alternative_to_improve,
    alternative_to_overcame,
    epsilon,
    allow_std,
    method,
    solutions_number,
):
    global proceed
    global improvement

    proceed = False
    warnings_children = html.Div([])
    is_open = False

    if alternative_to_improve is None or alternative_to_overcame is None:
        # print("Warning Fields: alternative_to_improve and alternative_to_overcome need to be filed")
        warnings_children = html.Div(
            [
                "Alternative_to_improve, alternative_to_overcome and features_to_change need to be filed"
            ]
        )
        is_open = True
        proceed = True
        improvement = None
        return None, warnings_children, is_open

    if n > 0:

        if epsilon is None:
            epsilon = 0.000001

        if allow_std is None:
            allow_std = False
        else:
            if allow_std == "True":
                allow_std = True
            else:
                allow_std = False

        no_exception = True

        try:
            improvement = buses_g.improvement(
                method,
                alternative_to_improve,
                alternative_to_overcame,
                epsilon,
                allow_std=allow_std,
                solutions_number=solutions_number,
            )
        except Exception as e:
            print(e)
            no_exception = False

        if no_exception:

            if improvement is None:
                proceed = True
                improvement = None
                # print("Warning no solution found")
                # raise PreventUpdate
                warnings_children = html.Div(["No solution found"])
                is_open = True
                return None, warnings_children, is_open

            rounded_improvement = improvement.applymap(formating)
            criteria_params = list(params_g[0].keys())
            params = pd.DataFrame.from_dict(params_g).set_index(criteria_params[0])
            raport = f"""
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
            """
            with open("html_report.html", "w") as f:
                f.write(raport)
            global raport_viz
            raport_viz = "visible"
            proceed = True
            return (
                dash_table.DataTable(
                    rounded_improvement.to_dict("records"),
                    [{"name": i, "id": i} for i in rounded_improvement.columns],
                    style_cell={"textAlign": "left"},
                    style_table={"overflowX": "auto"},
                ),
                warnings_children,
                is_open,
            )

    proceed = True
    improvement = None
    raise PreventUpdate


@app.callback(
    Output("improvement_std-result", "children"),
    Output("warning-main5-body", "children"),
    Output("warning-main5", "is_open"),
    [Input("apply-button", "n_clicks")],
    # Input('alternative-to-improve', 'value'),
    # Input('alternative-to-overcame', 'value'),
    State("alternative-to-improve", "value"),
    State("alternative-to-overcame", "value"),
    State("epsilon", "value"),
    State("choose-method", "value"),
    State("solutions-number", "value"),
    prevent_initial_call=True,
)
def improvement_std_results(
    n,
    alternative_to_improve,
    alternative_to_overcame,
    epsilon,
    method,
    solutions_number,
):
    global proceed
    proceed = False
    global improvement
    warnings_children = html.Div([])
    is_open = False

    if alternative_to_improve is None or alternative_to_overcame is None:
        # print("Warning Fields: alternative_to_improve and alternative_to_overcome need to be filed")
        warnings_children = html.Div(
            [
                "Alternative_to_improve, alternative_to_overcome and features_to_change need to be filed"
            ]
        )
        is_open = True
        proceed = True
        improvement = None
        return None, warnings_children, is_open

    if n > 0:

        if epsilon is None:
            epsilon = 0.000001

        no_exception = True

        try:
            improvement = buses_g.improvement(
                method,
                alternative_to_improve,
                alternative_to_overcame,
                epsilon,
                solutions_number=solutions_number,
            )
        except Exception as e:
            print(e)
            no_exception = False

        if no_exception:

            if improvement is None:
                proceed = True
                improvement = None
                # print("Warning no solution found")
                # raise PreventUpdate
                warnings_children = html.Div(["No solution found"])
                is_open = True
                return None, warnings_children, is_open

            rounded_improvement = improvement.applymap(formating)
            global raport_viz
            raport_viz = "visible"
            proceed = True
            return (
                dash_table.DataTable(
                    rounded_improvement.to_dict("records"),
                    [{"name": i, "id": i} for i in rounded_improvement.columns],
                    style_cell={"textAlign": "left"},
                    style_table={"overflowX": "auto"},
                ),
                warnings_children,
                is_open,
            )

    proceed = True
    improvement = None
    raise PreventUpdate


"""
@app.callback(
    Output('improvement-result', 'children'),
    [Input('apply-button', 'n_clicks')],
    #Input('alternative-to-improve', 'value'),
    #Input('alternative-to-overcame', 'value'),
    State('alternative-to-improve', 'value'),
    State('alternative-to-overcame', 'value'),
    State('features-to-change', 'value'),
    State('epsilon', 'value'),
    State('choose-method', 'value'),
    prevent_initial_call = True
)
def improvement_results(n, alternative_to_improve, alternative_to_overcame, features_to_change,epsilon, method):
    print(features_to_change)
    
    if n>0:
        global improvement
        improvement = buses_g.improvement(method, alternative_to_improve,alternative_to_overcame)
        return dash_table.DataTable(improvement.to_dict('records'), [{"name": i, "id": i} for i in improvement.columns])
    else:
        raise PreventUpdate
"""


def write_raport():
    criteria_params = list(params_g[0].keys())
    params = pd.DataFrame.from_dict(params_g).set_index(criteria_params[0])
    raport = f"""
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
    """
    with open("html_report.html", "w") as f:
        f.write(raport)


@app.callback(
    Output("viz", "children"),
    [Input("apply-button", "n_clicks")],
    # Input('alternative-to-improve', 'value'),
    State(component_id="alternative-to-improve", component_property="value"),
    prevent_initial_call=True,
)
def vizualization_change(n, alternative_to_improve):
    time.sleep(0.5)
    while True:
        if proceed:
            break
        time.sleep(0.5)
    if n > 0:
        df = buses_g.X_new.sort_values(agg_g, ascending=False) * np.append(
            buses_g.weights, [1, 1, 1]
        )
        # df = buses_g.X_new.sort_values('AggFn', ascending = False) * buses_g.weights
        df = df.applymap(formating)

        df = df.assign(Rank=None)
        columns = df.columns.tolist()
        columns = columns[-1:] + columns[:-1]
        df = df[columns]

        alternative_names = df.index.tolist()
        for alternative in alternative_names:
            df["Rank"][alternative] = (
                buses_g._ranked_alternatives.index(alternative) + 1
            )

        df.index.rename("Name", inplace=True)
        df.reset_index(inplace=True)
        # a = buses_g.plot(plot_name = title, color = colour_g)
        if improvement is None:
            raise PreventUpdate
        fig = buses_g.plot_improvement(alternative_to_improve, improvement)
        fig.write_image("chart.png")
        return html.Div(
            children=[
                dcc.Graph(id="vizualization", figure=fig),
                dash_table.DataTable(
                    df.to_dict("records"),
                    [{"name": i, "id": i} for i in df.columns],
                    sort_action="native",
                    style_cell={"textAlign": "left"},
                    style_table={"overflowX": "auto"},
                ),
            ]
        )
    else:
        raise PreventUpdate


# ==============================================================
#   MAIN
# ==============================================================

app.layout = dbc.Container(
    [
        header(app),
        dcc.Location(id="url", refresh=False),
        html.Div(id="page-content", className="container"),
        dcc.Store(id="data-store", storage_type="session"),
        dcc.Store(id="data-filename-store", storage_type="session"),
        dcc.Store(id="params-store", storage_type="session"),
        dcc.Store(id="params-filename-store", storage_type="session"),
        footer(),
    ],
    id="pad-layout",
    fluid=True,
)

app.title = "Postfactum Analysis Dashboard"
app._favicon = "img/pad_logo.png"

upload.get_callbacks(app)
criteria.get_callbacks(app)


@app.callback(
    Output("page-content", "children", allow_duplicate=True),
    Input("url", "pathname"),
    prevent_initial_call=True,
)
def display_page(pathname):
    if pathname == "/":
        return home.layout(app)
    elif pathname == "/upload":
        return upload.layout(app)
    elif pathname == "/criteria":
        return criteria.layout(app)
    elif pathname == "/main_dash_layout":
        return main_dash_layout()
    elif pathname == "/playground":
        return main_dash_layout2()
    else:
        return "404 - Page not found"


def parse_args():
    from argparse import ArgumentParser, BooleanOptionalAction
    from argparse import ArgumentDefaultsHelpFormatter

    parser = ArgumentParser(
        description="WMSD Dashboard server.",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--ip",
        type=str,
        default="127.0.0.1",
        help="The IP address the WMSD Dashboard server will listen on.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8050,
        help="The port the WMSD Dashboard server will listen on",
    )
    parser.add_argument(
        "--solver",
        type=str,
        default="scip",
        choices=["scip", "gurobi"],
        help="The nonlinear programming solver used to calculate the upper perimeter of the WMSD space.",
    )
    parser.add_argument(
        "--debug",
        default=True,
        action=BooleanOptionalAction,
        help="Turns on debugging option in run_server() method.",
    )

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = parse_args()
    if args.port == 443:
        app.run_server(
            debug=args.debug, host=args.ip, port=args.port, ssl_context="adhoc"
        )
    else:
        app.run_server(debug=args.debug, host=args.ip, port=args.port)
