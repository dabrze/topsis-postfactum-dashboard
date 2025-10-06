import pandas as pd
import dash
from dash import html, no_update, callback, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

from common.layout_elements import (
    HIDE,
    SHOW,
    create_criteria_table,
    settings_preview_default_message,
    stepper_layout,
    upload_card,
    data_preview_default_message,
    upload_default_message,
    styled_datatable,
)
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
            html.Div(
                "Upload files:", className="col-lg-12 section-header first-header"
            ),
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
                    title="JSON settings (optional)",
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
                html.Div("Dataset preview:", className="col-lg-12 section-header"),
                html.Div(
                    data_preview_default_message(),
                    id="upload-csv-data-preview",
                    className="col-lg-12",
                ),
            ],
            className="row block-row",
        ),
        html.Div(
            [
                html.Div("Settings preview:", className="col-lg-12 section-header"),
                html.Div(
                    settings_preview_default_message(),
                    id="upload-params-data-preview",
                    className="col-lg-12",
                ),
            ],
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
        # Store components to trigger extension error detection from JavaScript
        dcc.Store(id="csv-extension-error-store"),
        dcc.Store(id="json-extension-error-store"),
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("File Upload Error")),
                dbc.ModalBody(id="csv-error-message"),
                dbc.ModalFooter(
                    dbc.Button("Close", id="csv-error-close", className="ms-auto")
                ),
            ],
            id="csv-error-modal",
            is_open=False,
        ),
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("File Upload Error")),
                dbc.ModalBody(id="json-error-message"),
                dbc.ModalFooter(
                    dbc.Button("Close", id="json-error-close", className="ms-auto")
                ),
            ],
            id="json-error-modal",
            is_open=False,
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
        preview_msg = data_preview_default_message()
        upload_msg = upload_default_message()

        return preview_msg, False, upload_msg, HIDE, HIDE, True


@callback(
    Output("data-store", "data"),
    Output("data-filename-store", "data"),
    Output("csv-error-modal", "is_open"),
    Output("csv-error-message", "children"),
    Input("upload-csv-data", "contents"),
    State("upload-csv-data", "filename"),
)
def update_csv_data(file_data, file_name):
    if file_data is not None:
        try:
            df = parse_data_file(file_data, file_name)

            if df is not None:
                return df.to_dict("records"), file_name, False, ""
            else:
                return (
                    None,
                    None,
                    True,
                    "Unable to parse the file. Please check the file format.",
                )
        except Exception as e:
            error_message = str(e)
            if "File error:" in error_message:
                error_message = error_message.replace("File error: ", "")
            return None, None, True, f"Error reading file: {error_message}"
    else:
        return None, None, False, ""


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
    if params_dict is not None and file_name is not None:
        criteria_table = create_criteria_table(params_dict, disabled=True)

        return criteria_table, True, file_name, SHOW, SHOW
    else:
        preview_msg = settings_preview_default_message()
        upload_msg = upload_default_message()

        return preview_msg, False, upload_msg, HIDE, HIDE


@callback(
    Output("params-store", "data", allow_duplicate=True),
    Output("params-filename-store", "data", allow_duplicate=True),
    Output("json-error-modal", "is_open"),
    Output("json-error-message", "children"),
    Input("upload-params-data", "contents"),
    State("upload-params-data", "filename"),
    prevent_initial_call="initial_duplicate",
)
def update_params_data(file_data, file_name):
    if file_data is not None:
        try:
            params_dict = parse_params_file(file_data, file_name)

            if params_dict is not None:
                return params_dict, file_name, False, ""
            else:
                return (
                    None,
                    None,
                    True,
                    "Unable to parse the JSON file. Please check the file format.",
                )
        except Exception as e:
            error_message = str(e)
            if "File error:" in error_message:
                error_message = error_message.replace("File error: ", "")
            return None, None, True, f"Error reading file: {error_message}"

    return None, None, False, ""


@callback(
    Output("upload-params-data", "contents"),
    Input("upload-params-remove-btn", "n_clicks"),
)
def remove_params_file(n):
    if n is None:
        return no_update
    else:
        return None


@callback(
    Output("csv-error-modal", "is_open", allow_duplicate=True),
    Input("csv-error-close", "n_clicks"),
    State("csv-error-modal", "is_open"),
    prevent_initial_call=True,
)
def close_csv_error_modal(n, is_open):
    if n:
        return False
    return is_open


@callback(
    Output("json-error-modal", "is_open", allow_duplicate=True),
    Input("json-error-close", "n_clicks"),
    State("json-error-modal", "is_open"),
    prevent_initial_call=True,
)
def close_json_error_modal(n, is_open):
    if n:
        return False
    return is_open


@callback(
    Output("csv-error-modal", "is_open", allow_duplicate=True),
    Output("csv-error-message", "children", allow_duplicate=True),
    Input("csv-extension-error-store", "data"),
    prevent_initial_call=True,
)
def show_csv_extension_error(error_data):
    if error_data and "error" in error_data:
        return True, error_data["error"]
    return no_update, no_update


@callback(
    Output("json-error-modal", "is_open", allow_duplicate=True),
    Output("json-error-message", "children", allow_duplicate=True),
    Input("json-extension-error-store", "data"),
    prevent_initial_call=True,
)
def show_json_extension_error(error_data):
    if error_data and "error" in error_data:
        return True, error_data["error"]
    return no_update, no_update
