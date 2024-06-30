import base64
import json
import pandas as pd
import numpy as np

from dash import html
from dash import dcc
from dash import dash_table
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash import no_update

from components.common import HIDE, SHOW, stepper_layout, styled_datatable
from processing.data_functions import parse_data_file, parse_params_file


def upload_default_message():
    return [
        html.Br(),
        html.I(className="fa-solid fa-cloud-arrow-up"),
        " Drop file here or",
        html.Br(),
        "click to upload...",
    ]


def preview_default_message():
    return html.Span("Upload data to see preview", className="help-msg")


def upload_card(
    title,
    upload_id,
    message_div_id,
    checkmark_div_id,
    remove_btn_id,
    filetypes,
    multiple=False,
    optional=False,
):
    addional_class = "optional" if optional else ""

    return html.Div(
        html.Div(
            html.Div(
                [
                    html.H5(title, className="card-title"),
                    dcc.Upload(
                        [
                            html.Div(
                                upload_default_message(),
                                className="dz-default dz-message",
                                id=f"{message_div_id}",
                            ),
                            html.Div(
                                html.I(className="fas fa-check"),
                                className="dz-success-mark",
                                style={"display": "none"},
                                id=f"{checkmark_div_id}",
                            ),
                            html.A(
                                id=f"{remove_btn_id}",
                                className="dz-remove",
                                children="Remove file",
                                style={"display": "none"},
                            ),
                        ],
                        multiple=multiple,
                        accept=f"{filetypes}",
                        className="dropzone dz-clickable",
                        id=upload_id,
                        max_size=2000000,  # 2MB
                    ),
                ],
                className="card-body",
            ),
            className=f"card drop-card {addional_class}",
        ),
        className="col-lg-6",
    )


def layout(app):
    """
    Generates the layout for the home page of the TOPSIS Postfactum Dashboard.

    Args:
        app (dash.Dash): The Dash application object.

    Returns:
        dash.html.Div: The generated HTML layout for the home page.
    """
    return stepper_layout(
        app,
        step2_state="active",
        show_background=False,
        content=[
            html.Div(
                html.Div("Upload files:", className="col-lg-12 block-row"),
                className="row",
            ),
            html.Div(
                [
                    upload_card(
                        title="CSV or Excel",
                        upload_id="upload-csv-data",
                        message_div_id="upload-csv-message",
                        checkmark_div_id="upload-csv-checkmark",
                        remove_btn_id="upload-csv-remove-btn",
                        filetypes=".csv, .xls, .xlsx",
                    ),
                    upload_card(
                        title="JSON parameters (optional)",
                        upload_id="upload-params-data",
                        message_div_id="upload-params-message",
                        checkmark_div_id="upload-params-checkmark",
                        remove_btn_id="upload-params-remove-btn",
                        filetypes=".json",
                        optional=True,
                    ),
                ],
                className="row block-row",
            ),
            html.Div(
                [
                    html.Div("Dataset preview:", className="col-lg-12 block-row"),
                    html.Div(
                        preview_default_message(),
                        id="upload-csv-data-preview",
                        className="col-lg-12",
                    ),
                ],
                className="row block-row",
            ),
            html.Div(
                html.Div(id="upload-params-data-preview", className="col-lg-12"),
                className="row block-row",
            ),
            html.Div(
                [
                    html.A(
                        html.Button(
                            "Previous",
                            className="btn btn-primary me-1",
                        ),
                        href="/",
                    ),
                    html.A(
                        html.Button(
                            "Next",
                            id="upload-submit-btn",
                            className="btn btn-primary",
                            disabled=True,
                        ),
                        href="/criteria",
                    ),
                ],
                className="stepper-form-controls",
            ),
        ],
    )


def get_callbacks(app):
    @app.callback(
        Output("upload-csv-data-preview", "children"),
        Output("upload-csv-data", "disable_click"),
        Output("upload-csv-message", "children"),
        Output("upload-csv-checkmark", "style"),
        Output("upload-csv-remove-btn", "style"),
        Output("upload-submit-btn", "disabled"),
        Output("data-store", "data"),
        Input("upload-csv-data", "contents"),
        State("upload-csv-data", "filename"),
    )
    def update_csv_data(file_data, file_name):
        if file_data is not None:
            df, message = parse_data_file(file_data, file_name)

            if df is not None:
                table = styled_datatable(df)

                return table, True, file_name, SHOW, SHOW, False, df.to_dict("records")
            else:
                return preview_default_message(), False, message, HIDE, HIDE, True, None
        else:
            preview_msg = preview_default_message()
            upload_msg = upload_default_message()

            return preview_msg, False, upload_msg, HIDE, HIDE, True, None

    @app.callback(
        Output("upload-csv-data", "contents"),
        Input("upload-csv-remove-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def remove_data_file(n):
        if n is None:
            return no_update
        else:
            return None

    @app.callback(
        Output("upload-params-data-preview", "children"),
        Output("upload-params-data", "disable_click"),
        Output("upload-params-message", "children"),
        Output("upload-params-checkmark", "style"),
        Output("upload-params-remove-btn", "style"),
        Output("params-store", "data"),
        Input("upload-params-data", "contents"),
        State("upload-params-data", "filename"),
    )
    def update_params_data(file_data, file_name):
        if file_data is not None:
            params_dict, message = parse_params_file(file_data, file_name)

            if params_dict is not None:
                return None, True, file_name, SHOW, SHOW, params_dict
            else:
                return None, False, message, HIDE, HIDE, None
        else:
            return None, False, upload_default_message(), HIDE, HIDE, None

    @app.callback(
        Output("upload-params-data", "contents"),
        Input("upload-params-remove-btn", "n_clicks"),
    )
    def remove_params_file(n):
        if n is None:
            return no_update
        else:
            return None
