import dash
from dash import html, dcc, callback
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import WMSDTransformer as wmsdt

from common import server_setup
from common.data_functions import extract_settings_from_dict, prepare_wmsd_data
from common.layout_elements import data_preview_default_message, styled_datatable

dash.register_page(
    __name__,
    title="Postfactum Analysis Dashboard: Analyze",
    description="TOPSIS visualization and postfactum analysis dashboard.",
    image="img/pad_logo.png",
)


def layout(dataset=None):
    return html.Div(
        [
            dbc.Tabs(
                [
                    dbc.Tab(
                        label="Ranking visualization",
                        children=[
                            html.Div(
                                dcc.Loading(
                                    dcc.Graph(id="ranking-fig", className="col-lg-12")
                                ),
                                className="row",
                            ),
                            html.Div(
                                dcc.Loading(
                                    html.Div(
                                        id="ranking-datatable", className="col-lg-12"
                                    )
                                ),
                                className="row",
                            ),
                        ],
                        tab_class_name="dashboard-tab ",
                        label_class_name="dashboard-tab-label ranking-tab",
                    ),
                    dbc.Tab(
                        label="Postfactum analysis",
                        children=["TODO: Postfactum analysis"],
                        tab_class_name="dashboard-tab",
                        label_class_name="dashboard-tab-label pad-tab",
                    ),
                    dbc.Tab(
                        label="Settings and export",
                        children=["TODO: Settings and export"],
                        tab_class_name="dashboard-tab",
                        label_class_name="dashboard-tab-label settings-tab",
                    ),
                ],
                class_name="dashboard-tabs nav-fill",
            ),
        ],
        className="row",
    )


@callback(
    Output("ranking-fig", "figure"),
    Output("ranking-datatable", "children"),
    Input("data-store", "data"),
    State("data-filename-store", "data"),
    Input("params-store", "data"),
)
def update_from_store(store_data, filename, params_dict):
    if store_data is not None:
        df = pd.DataFrame.from_dict(store_data)
        table = styled_datatable(df)
        df, expert_ranges, weights, objectives = prepare_wmsd_data(df, params_dict)

        wmsd = wmsdt.WMSDTransformer(wmsdt.RTOPSIS, server_setup.SOLVER)
        wmsd.fit_transform(df, weights, objectives, expert_ranges)
        fig = wmsd.plot(plot_name="")

        return fig, table
    else:
        return None, data_preview_default_message()
