import pandas as pd
import dash
from dash import html, dcc, no_update, callback
from dash.dependencies import Input, Output, State

from common.layout_elements import *
from common.data_functions import parse_data_file, parse_params_file


dash.register_page(
    __name__,
    title="Postfactum Analysis Dashboard: Upload data",
    description="TOPSIS visualization and postfactum analysis dashboard.",
    image="img/pad_logo.png",
)

layout = stepper_layout(
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


@callback(
    Output("upload-csv-data-preview", "children"),
    Output("upload-csv-data", "disable_click"),
    Output("upload-csv-message", "children"),
    Output("upload-csv-checkmark", "style"),
    Output("upload-csv-remove-btn", "style"),
    Output("upload-submit-btn", "disabled"),
    Input("data-store", "data"),
    State("data-filename-store", "data"),
)
def update_csv_store(store_data, file_name):
    if store_data is not None or file_name is not None:
        df = pd.DataFrame.from_dict(store_data)
        table = styled_datatable(df)

        return table, True, file_name, SHOW, SHOW, False
    else:
        preview_msg = preview_default_message()
        upload_msg = upload_default_message()

        return preview_msg, False, upload_msg, HIDE, HIDE, True


@callback(
    Output("data-store", "data"),
    Output("data-filename-store", "data"),
    Input("upload-csv-data", "contents"),
    State("upload-csv-data", "filename"),
)
def update_csv_data(file_data, file_name):
    if file_data is not None:
        df, message = parse_data_file(file_data, file_name)

        if df is not None:
            return df.to_dict("records"), file_name
        else:
            return None, None
    else:
        return None, None


@callback(
    Output("upload-csv-data", "contents"),
    Input("upload-csv-remove-btn", "n_clicks"),
)
def remove_data_file(n):
    if n is None:
        return no_update
    else:
        return None


@callback(
    Output("upload-params-data-preview", "children"),
    Output("upload-params-data", "disable_click"),
    Output("upload-params-message", "children"),
    Output("upload-params-checkmark", "style"),
    Output("upload-params-remove-btn", "style"),
    Input("params-store", "data"),
    State("params-filename-store", "data"),
)
def update_params_store(params_dict, file_name):
    if params_dict is not None or file_name is not None:
        return None, True, file_name, SHOW, SHOW
    else:
        return None, False, upload_default_message(), HIDE, HIDE


@callback(
    Output("params-store", "data"),
    Output("params-filename-store", "data"),
    Input("upload-params-data", "contents"),
    State("upload-params-data", "filename"),
)
def update_params_data(file_data, file_name):
    if file_data is not None:
        params_dict, message = parse_params_file(file_data, file_name)

        if params_dict is not None:
            return params_dict, file_name

    return None, None


@callback(
    Output("upload-params-data", "contents"),
    Input("upload-params-remove-btn", "n_clicks"),
)
def remove_params_file(n):
    if n is None:
        return no_update
    else:
        return None
