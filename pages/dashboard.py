import json
import dash
from dash import html, dcc, callback
from dash.dependencies import Input, Output, State, ALL, MATCH
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import WMSDTransformer as wmsdt

from common import server_setup
from common.data_functions import prepare_wmsd_data
from common.layout_elements import (
    OVERLAY_STYLE,
    create_spinner,
    data_preview_default_message,
    stepper_layout,
    styled_datatable,
)

DEFAULT_PRECISION = 3
DEFAULT_COLORSCALE = "jet"

dash.register_page(
    __name__,
    title="Postfactum Analysis Dashboard: Analyze",
    description="TOPSIS visualization and postfactum analysis dashboard.",
    image="img/pad_logo.png",
)


def layout(dataset=None):
    return stepper_layout(
        step4_state="active",
        show_background=False,
        content=html.Div(
            html.Div(
                [
                    dbc.Tabs(
                        [
                            visualization_tab(),
                            analysis_tab(),
                            settings_tab(dataset),
                        ],
                        class_name="dashboard-tabs nav-fill",
                    ),
                    dbc.Input(id="dashboard-query-param", type="hidden", value=dataset),
                ],
                className="col-lg-12",
            ),
            className="row",
        ),
    )


def visualization_tab():
    return dbc.Tab(
        label="Ranking visualization",
        children=[
            html.Div(
                dcc.Loading(
                    dcc.Graph(id="ranking-fig", className="col-lg-12"),
                    overlay_style=OVERLAY_STYLE,
                    custom_spinner=create_spinner("Loading WMSD visualization..."),
                ),
                className="row",
            ),
            html.Div(
                dcc.Loading(
                    html.Div(
                        id="ranking-datatable",
                        className="col-lg-12",
                    ),
                    overlay_style=OVERLAY_STYLE,
                    custom_spinner=create_spinner("Loading dataset..."),
                ),
                className="row",
            ),
        ],
        tab_class_name="dashboard-tab ",
        label_class_name="dashboard-tab-label ranking-tab",
    )


def postfactum_analysis_card(id, df, precision, colorscale):
    return html.Div(
        children=[
            html.Div(
                html.Div(
                    [
                        html.Div(
                            f"Postfactum analysis #{id}", className="col text-start"
                        ),
                        html.Div(
                            html.I(
                                className="fa fa-times",
                                id={"type": "postfactum-close-icon", "index": id},
                            ),
                            className="col text-end close-icon",
                        ),
                    ],
                    className="row",
                ),
                className="card-header container-fluid",
            ),
            html.Div(
                dbc.Tabs(
                    [
                        dbc.Tab(
                            postfactum_target_tab(id, df, precision),
                            label="Analysis target",
                        ),
                        dbc.Tab(postfactum_method_tab(id), label="Method and options"),
                        dbc.Tab(postfactum_results_tab(id), label="Results"),
                    ]
                ),
                className="card-body postfactum-steps",
            ),
        ],
        id={"type": "postfactum-analysis", "index": id},
        className="card mb-3",
    )


def postfactum_target_tab(id, df, precision):
    return [
        dbc.Row(
            html.P(
                [
                    "Choose the ",
                    html.B("source"),
                    " alternative you want to change and the ",
                    html.B("target"),
                    " alternative you aim to supersede. We will find ways to change the source alternative to "
                    "be as good or slightly better than the target alternative (according to TOPSIS).",
                ]
            )
        ),
        dbc.Row(
            [
                html.H4("Source alternative", className="col-md-6"),
                html.H4("Target alternative", className="col-md-6"),
            ]
        ),
        dbc.Row(
            [
                html.Div(
                    styled_datatable(df, precision, row_selectable="single"),
                    className="col-md-6",
                ),
                html.Div(
                    styled_datatable(df, precision, row_selectable="single"),
                    className="col-md-6",
                ),
            ]
        ),
    ]


def postfactum_method_tab(id):
    return html.Div("method")


def postfactum_results_tab(id):
    return html.Div("results")


def analysis_tab():
    return dbc.Tab(
        label="Postfactum analysis",
        children=[
            html.Button(
                [
                    html.I(className="fa-solid fa-plus"),
                    html.Br(),
                    "Add postfactum analysis",
                ],
                className="btn btn-outline-primary btn-lg text-center w-100 mt-3",
                id="add-postfactum-analysis-btn",
            ),
        ],
        tab_class_name="dashboard-tab",
        label_class_name="dashboard-tab-label pad-tab",
        id="postfactum-analysis-tab",
    )


def settings_tab(dataset):
    return dbc.Tab(
        label="Settings and export",
        children=[
            html.Div(
                [
                    html.Div(
                        [
                            html.H4("Settings", className="section-h4"),
                            dbc.Label(
                                "Choose the color scale for the ranking visualization:"
                            ),
                            dbc.Select(
                                options=px.colors.named_colorscales(),
                                value=DEFAULT_COLORSCALE,
                                id="colorscale-dropdown",
                                className="form-control",
                            ),
                            dcc.Graph(id="colorscale-preview"),
                            html.P(),
                            dbc.Label("Choose the decimal precision used in tables:"),
                            dbc.Input(
                                id="precision-input",
                                value=DEFAULT_PRECISION,
                                type="number",
                                min=0,
                                className="form-control",
                            ),
                            html.P(),
                            html.A(
                                html.Button(
                                    [
                                        html.I(
                                            className="fa-solid fa-arrows-rotate btn-icon"
                                        ),
                                        "Apply changes",
                                    ],
                                    id="apply-changes-btn",
                                    className="btn btn-primary",
                                ),
                                href="/dashboard"
                                + (f"?dataset={dataset}" if dataset else ""),
                            ),
                        ],
                        className="col-lg-6",
                    ),
                    html.Div(
                        [
                            html.H4("Export", className="section-h4"),
                            html.P(
                                "To perform a similar analysis in the future with the same weights, value ranges, "
                                "and criteria types, you can download the JSON settings file. The next time you "
                                "upload a dataset, you can upload the settings file to apply the same settings."
                            ),
                            html.Button(
                                [
                                    html.I(className="fa-solid fa-download btn-icon"),
                                    "Download JSON settings",
                                ],
                                id="download-params-btn",
                                className="btn btn-primary",
                            ),
                            dcc.Download(id="download-params"),
                            html.Br(),
                            html.Br(),
                            html.P(
                                "To share the results of the analysis, you can download an HTML report. Containing "
                                "the ranking visualization, the dataset, and a list of all the performed postfactum "
                                "analyses."
                            ),
                            html.Button(
                                [
                                    html.I(
                                        className="fa-solid fa-file-export btn-icon"
                                    ),
                                    "Download Report",
                                ],
                                disabled=True,
                                id="download-report-btn",
                                className="btn btn-primary",
                            ),
                            dcc.Download(id="download-report"),
                        ],
                        className="col-lg-6",
                    ),
                ],
                className="row",
            )
        ],
        tab_class_name="dashboard-tab",
        label_class_name="dashboard-tab-label settings-tab",
    )


def extract_data_from_store(
    query_param, store_data, params_dict, precision, colorscale, plot=False
):
    if precision is None:
        precision = DEFAULT_PRECISION
    if colorscale is None:
        colorscale = DEFAULT_COLORSCALE

    if query_param == "playground":
        df = pd.read_csv("data/students.csv")

        with open("data/students_settings.json") as f:
            params_dict = json.load(f)
    elif store_data is not None:
        df = pd.DataFrame.from_dict(store_data)

    if df is not None:
        wmsd_df, expert_ranges, weights, objectives = prepare_wmsd_data(df, params_dict)
        wmsd = wmsdt.WMSDTransformer(wmsdt.RTOPSIS, server_setup.SOLVER)
        wmsd_df = wmsd.fit_transform(wmsd_df, weights, objectives, expert_ranges)

        df.loc[:, "WM"] = wmsd_df.loc[:, "Mean"].values
        df.loc[:, "WSD"] = wmsd_df.loc[:, "Std"].values
        df.loc[:, "TOPSIS Score [R(v)]"] = wmsd_df.loc[:, "R"].values
        df = df.sort_values("TOPSIS Score [R(v)]", ascending=False)
        df.insert(0, "Rank", range(1, df.shape[0] + 1))

        if plot is True:
            fig = wmsd.plot(plot_name="", color=colorscale)
        else:
            fig = None

    return df, precision, colorscale, params_dict, fig


@callback(
    Output("ranking-fig", "figure"),
    Output("ranking-datatable", "children"),
    Output("precision-input", "value"),
    Output("colorscale-dropdown", "value"),
    Input("dashboard-query-param", "value"),
    Input("data-store", "data"),
    Input("data-filename-store", "data"),
    Input("params-store", "data"),
    Input("precision-store", "data"),
    Input("colorscale-store", "data"),
)
def update_from_store(
    query_param, store_data, filename, params_dict, precision, colorscale
):
    df, precision, colorscale, params_dict, fig = extract_data_from_store(
        query_param, store_data, params_dict, precision, colorscale, plot=True
    )

    if df is not None:
        table = styled_datatable(df, precision=precision)

        return fig, table, precision, colorscale
    else:
        return (
            None,
            data_preview_default_message(),
            DEFAULT_PRECISION,
            DEFAULT_COLORSCALE,
        )


@callback(
    Output("download-params", "data"),
    Input("download-params-btn", "n_clicks"),
    State("data-filename-store", "data"),
    State("params-store", "data"),
    prevent_initial_call=True,
)
def download_params_dict(n_clicks, data_filename, params_dict):
    json_filename = data_filename.split(".")[0] + "_settings.json"

    return dict(content=json.dumps(params_dict, indent=4), filename=json_filename)


@callback(
    Output("colorscale-preview", "figure"),
    Input("colorscale-dropdown", "value"),
)
def change_colorscale_preview(scale):
    trace = go.Heatmap(z=np.linspace(0, 1, 1000).reshape(1, -1), showscale=False)

    layout = go.Layout(
        height=50,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        clickmode="none",
    )
    trace["colorscale"] = scale
    fig = {"data": [trace], "layout": layout}
    return fig


@callback(
    Output("precision-store", "data"),
    Output("colorscale-store", "data"),
    Input("apply-changes-btn", "n_clicks"),
    State("precision-input", "value"),
    State("colorscale-dropdown", "value"),
    prevent_initial_call=True,
)
def change_precision(n_clicks, precision, colorscale):
    if n_clicks is not None and n_clicks > 0:
        return precision, colorscale
    else:
        return dash.no_update, dash.no_update


@callback(
    Output("postfactum-analysis-tab", "children"),
    Input("add-postfactum-analysis-btn", "n_clicks"),
    State("postfactum-analysis-tab", "children"),
    State("data-store", "data"),
    State("precision-store", "data"),
    State("colorscale-store", "data"),
    State("dashboard-query-param", "value"),
    State("params-store", "data"),
    prevent_initial_call=True,
)
def add_postfactum_analysis_card(
    n_clicks,
    current_analyses,
    store_data,
    precision,
    colorscale,
    query_param,
    params_dict,
):
    if n_clicks is not None and n_clicks > 0:
        df, precision, colorscale, params_dict, fig = extract_data_from_store(
            query_param, store_data, params_dict, precision, colorscale, plot=True
        )

        new_card = postfactum_analysis_card(n_clicks, df, precision, colorscale)
        current_analyses.insert(-1, new_card)

        return current_analyses
    else:
        dash.no_update


@callback(
    Output({"type": "postfactum-analysis", "index": MATCH}, "children"),
    Output({"type": "postfactum-analysis", "index": MATCH}, "style"),
    Input({"type": "postfactum-close-icon", "index": MATCH}, "n_clicks"),
    prevent_initial_call=True,
)
def remove_postfactum_analysis_card(n_clicks):
    if n_clicks is not None:
        return None, dict(display="none", margin=0)
    else:
        dash.no_update, dash.no_update
