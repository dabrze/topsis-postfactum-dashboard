import base64
import json
import io
import pandas as pd
import numpy as np
import csv

from dash import html
from dash import dcc
from dash import dash_table
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash import no_update

from components.common import stepper_layout


def upload_default_message():
    return [
        html.I(className="fa-solid fa-cloud-arrow-up"),
        " Drop file here or",
        html.Br(),
        "click to upload...",
    ]


def upload_card(
    title,
    upload_id,
    store_id,
    message_div_id,
    remove_btn_id,
    filetypes,
    multiple=False,
    optional=False,
):
    """
    Create a card component with an upload feature.

    Parameters:
    title (str): The title of the card.
    upload_id (str): The ID of the upload component.
    store_id (str): The ID of the store component.
    multiple (bool, optional): Whether multiple files can be uploaded. Defaults to False.
    optional (bool, optional): Whether the upload is optional. Defaults to False.

    Returns:
    dash_html_components.Div: The card component with the upload feature.
    """
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
                        max_size=10000000,  # 10MB
                    ),
                    dcc.Store(
                        id=store_id,
                        data=None,
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
                        store_id="upload-csv-store",
                        message_div_id="upload-csv-message",
                        remove_btn_id="upload-csv-remove-btn",
                        filetypes=".csv, .xls, .xlsx",
                    ),
                    upload_card(
                        title="JSON parameters (optional)",
                        upload_id="upload-params-data",
                        store_id="upload-params-store",
                        message_div_id="upload-params-message",
                        remove_btn_id="upload-params-remove-btn",
                        filetypes=".json",
                        optional=True,
                    ),
                ],
                className="row block-row",
            ),
            html.Div(
                [
                    html.Div(id="upload-csv-data-preview"),
                    html.Div(id="upload-params-data-preview"),
                ],
                id="data-preview-content",
            ),
            html.Div(
                html.Button(
                    "Submit",
                    id="upload-submit-btn",
                    className="submit-button",
                    style={"display": "none"},
                ),
                id="nav-buttons",
            ),
        ],
    )


def get_delimiter(data):
    sniffer = csv.Sniffer()
    data = data.decode("utf-8")
    delimiter = sniffer.sniff(data).delimiter
    return delimiter


def parse_data_file(contents, filename):
    df = None
    message = ""

    try:
        if filename.endswith(".csv"):
            content_type, content_string = contents.split(",")
            decoded = base64.b64decode(content_string)
            sep = get_delimiter(decoded)
            if sep == ";":
                decimal = ","
            else:
                decimal = "."

            df = pd.read_csv(
                io.StringIO(decoded.decode("utf-8")), sep=sep, decimal=decimal
            )
        elif filename.endswith(".xls") or filename.endswith(".xlsx"):
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            message = "Please upload a CSV or Excel file."
    except Exception as e:
        message = f"File error: {e}"

    return df, message


def get_callbacks(app):
    @app.callback(
        Output("upload-csv-data-preview", "children", allow_duplicate=True),
        Output("upload-csv-data", "disable_click", allow_duplicate=True),
        Output("upload-csv-message", "children", allow_duplicate=True),
        Output("upload-csv-remove-btn", "style", allow_duplicate=True),
        Output("upload-submit-btn", "style", allow_duplicate=True),
        Input("upload-csv-data", "contents"),
        State("upload-csv-data", "filename"),
        prevent_initial_call=True,
    )
    def update_csv_data(file_data, file_name):
        if file_data is not None:
            df, message = parse_data_file(file_data, file_name)

            if df is not None:
                preview = html.Div(
                    [
                        dash_table.DataTable(
                            data=df.to_dict("records"),
                            columns=[{"name": i, "id": i} for i in df.columns],
                            style_cell={"textAlign": "left"},
                            page_size=8,
                        ),
                        dcc.Store(id="upload-csv-store", data=df.to_dict("records")),
                    ]
                )

                return (
                    preview,
                    True,
                    file_name,
                    {"display": "block"},
                    {"display": "block"},
                )
            else:
                return (None, False, message, {"display": "none"}, {"display": "none"})
        else:
            raise PreventUpdate

    @app.callback(
        Output("upload-csv-message", "children", allow_duplicate=True),
        Output("upload-csv-data", "disable_click", allow_duplicate=True),
        Output("upload-csv-data", "contents", allow_duplicate=True),
        Output("upload-csv-data-preview", "children", allow_duplicate=True),
        Output("upload-csv-remove-btn", "style", allow_duplicate=True),
        Output("upload-submit-btn", "style", allow_duplicate=True),
        Input("upload-csv-remove-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def remove_data_file(n):
        if n is None:
            return no_update
        else:
            msg = upload_default_message()
            return msg, False, None, None, {"display": "none"}, {"display": "none"}

    @app.callback(
        Output("upload-params-data-preview", "children", allow_duplicate=True),
        Output("upload-params-message", "children"),
        Output("upload-params-remove-btn", "children", allow_duplicate=True),
        Input("upload-params-data", "contents"),
        State("upload-params-data", "filename"),
        State("upload-params-data", "last_modified"),
        prevent_initial_call=True,
    )
    def update_wizard_data_output_params(contents_params, name_params, date_params):

        if contents_params is not None:
            child = [
                parse_file_wizard_data_params(c, n, d)[0]
                for c, n, d in zip([contents_params], [name_params], [date_params])
            ]

            warnings_children = [
                parse_file_wizard_data_params(c, n, d)[1]
                for c, n, d in zip([contents_params], [name_params], [date_params])
            ][0]
            is_open = [
                parse_file_wizard_data_params(c, n, d)[2]
                for c, n, d in zip([contents_params], [name_params], [date_params])
            ][0]
            remove = html.Button(
                id="wizard_data_input_remove-params-button",
                className="remove-button",
                children="Remove",
            )
            return child, name_params, remove
        else:
            raise PreventUpdate

    @app.callback(
        Output("wizard-data-input-remove-upload-params", "children"),
        Output("upload-params-data-preview", "children"),
        Output("upload-params-remove-btn", "children"),
        Input("wizard_data_input_remove-params-button", "n_clicks"),
    )
    def remove_file_wizard_data_params_file(n):

        if n is None:
            return no_update

        child = [
            html.Div("Upload data"),
            dcc.Store(id="upload-params-store", data=None),
            dcc.Upload(
                id="upload-params-data",
                children=html.Div(
                    ["Drag and Drop or Select Files"],
                    id="upload-params-message",
                ),
                multiple=False,
            ),
            html.Div(id="upload-params-remove-btn"),
        ]
        table = None
        remove = None
        return child, table, remove


def parse_file_wizard_data_params(contents, filename, date):
    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)
    warnings_children = html.Div([])
    is_open = False

    try:
        if filename.endswith(".json"):
            content_dict = json.loads(decoded)
            global params_g
            params_g = content_dict
        else:
            # return "Prevent update - Please upload a file with the .json extension"
            warnings_children = html.Div(
                ["Please upload a file with the .json extension"]
            )
            is_open = True
            return html.Div([]), warnings_children, is_open
    except Exception as e:
        # print(e)
        warnings_children = html.Div(["There was an error processing this file."])
        is_open = True
        return html.Div([]), warnings_children, is_open

    return (
        html.Div(
            [
                dcc.Store(id="upload-params-store", data=content_dict),
            ]
        ),
        warnings_children,
        is_open,
    )


def check_parameters_wizard_data_files(data, params, param_keys):

    criteria = list(data[0].keys())

    df_data = pd.DataFrame.from_dict(data).set_index(criteria[0])
    df_params = pd.DataFrame.from_dict(params)

    n_alternatives = df_data.shape[0]
    m_criteria = df_data.shape[1]

    if param_keys[1] in df_params:
        if len(df_params[param_keys[1]]) != m_criteria:
            if args.debug:
                print("Invalid value 'weights'.")
            return -1
        if not all(
            type(item) in [int, float, np.float64] for item in df_params[param_keys[1]]
        ):
            if args.debug:
                print(
                    "Invalid value 'weights'. Expected numerical value (int or float)."
                )
            return -1
        if not all(item >= 0 for item in df_params[param_keys[1]]):
            if args.debug:
                print("Invalid value 'weights'. Expected value must be non-negative.")
            return -1
        if not any(item > 0 for item in df_params[param_keys[1]]):
            if args.debug:
                print("Invalid value 'weights'. At least one weight must be positive.")
            return -1
    else:
        return -1

    if param_keys[4] in df_params:
        if len(df_params[param_keys[4]]) != m_criteria:
            if args.debug:
                print("Invalid value 'objectives'.")
            return -1
        if not all(item in ["min", "max"] for item in df_params[param_keys[4]]):
            if args.debug:
                print(
                    "Invalid value at 'objectives'. Use 'min', 'max', 'gain', 'cost', 'g' or 'c'."
                )
            return -1
    else:
        return -1

    if param_keys[2] in df_params and param_keys[3] in df_params:
        if len(df_params[param_keys[2]]) != m_criteria:
            if args.debug:
                print(
                    "Invalid value at 'expert_range'. Length of should be equal to number of criteria."
                )
            return -1
        if len(df_params[param_keys[3]]) != m_criteria:
            if args.debug:
                print(
                    "Invalid value at 'expert_range'. Length of should be equal to number of criteria."
                )
            return -1
        if not all(
            type(item) in [int, float, np.float64] for item in df_params[param_keys[2]]
        ):
            if args.debug:
                print(
                    "Invalid value at 'expert_range'. Expected numerical value (int or float)."
                )
            return -1
        if not all(
            type(item) in [int, float, np.float64] for item in df_params[param_keys[3]]
        ):
            if args.debug:
                print(
                    "Invalid value at 'expert_range'. Expected numerical value (int or float)."
                )
            return -1

        lower_bound = df_data.min()
        upper_bound = df_data.max()

        for lower, upper, mini, maxi in zip(
            lower_bound, upper_bound, df_params[param_keys[2]], df_params[param_keys[3]]
        ):
            if mini > maxi:
                if args.debug:
                    print(
                        "Invalid value at 'expert_range'. Minimal value  is bigger then maximal value."
                    )
                return -1
            if lower < mini:
                if args.debug:
                    print(
                        "Invalid value at 'expert_range'. All values from original data must be in a range of expert_range."
                    )
                return -1
            if upper > maxi:
                if args.debug:
                    print(
                        "Invalid value at 'expert_range'. All values from original data must be in a range of expert_range."
                    )
                return -1
    else:
        return -1

    return 1


def return_columns_wizard_parameters_params_table(param_keys):
    columns = [
        {"id": "criterion", "name": "Criterion", "type": "text", "editable": False},
        {"id": param_keys[1], "name": "Weight", "type": "numeric"},
        {"id": param_keys[2], "name": "Expert Min", "type": "numeric"},
        {"id": param_keys[3], "name": "Expert Max", "type": "numeric"},
        {"id": param_keys[4], "name": "Objective", "presentation": "dropdown"},
    ]

    return columns


def fill_parameters_wizard_parameters_params(params, df, param_keys):

    if params is None:
        m_criteria = df.shape[1]
        return np.ones(m_criteria), df.min(), df.max(), np.repeat("max", m_criteria)
    else:
        weights = list(params[param_keys[1]].values())
        mins = list(params[param_keys[2]].values())
        maxs = list(params[param_keys[3]].values())
        objectives = list(params[param_keys[4]].values())

        return weights, mins, maxs, objectives
