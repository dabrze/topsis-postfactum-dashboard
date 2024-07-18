import json
import dash
from dash import html, dcc, callback
from dash.dependencies import Input, Output, State
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
                            settings_tab(),
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


def analysis_tab():
    return dbc.Tab(
        label="Postfactum analysis",
        children=["TODO: Postfactum analysis"],
        tab_class_name="dashboard-tab",
        label_class_name="dashboard-tab-label pad-tab",
    )


def settings_tab():
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
                                value="jet",
                                id="colorscale-dropdown",
                                className="form-control",
                            ),
                            dcc.Graph(id="colorscale-preview"),
                            html.P(),
                            dbc.Label("Choose the decimal precision used in tables:"),
                            dbc.Input(
                                id="precision-input",
                                value=3,
                                type="number",
                                min=0,
                                className="form-control",
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


@callback(
    Output("ranking-fig", "figure"),
    Output("ranking-datatable", "children"),
    Input("dashboard-query-param", "value"),
    Input("data-store", "data"),
    State("data-filename-store", "data"),
    Input("params-store", "data"),
)
def update_from_store(query_param, store_data, filename, params_dict):
    if query_param == "playground":
        df = pd.read_csv("data/students.csv")
        filename = "students.csv"

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

        fig = wmsd.plot(plot_name="")
        table = styled_datatable(df)

        return fig, table
    else:
        return None, data_preview_default_message()


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
def change_colorscale(scale):
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
