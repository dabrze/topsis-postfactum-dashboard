import pandas as pd
import dash
from dash import html, dcc, no_update, callback
from dash.dependencies import Input, Output, State, MATCH, ALL

from common.data_functions import (
    create_default_params_dict,
    parse_params_file,
)
from common.layout_elements import (
    INVISIBLE,
    NO_STYLE,
    create_criteria_table,
    stepper_layout,
)


dash.register_page(
    __name__,
    title="Postfactum Analysis Dashboard: Upload data",
    description="TOPSIS visualization and postfactum analysis dashboard.",
    image="img/pad_logo.png",
)

layout = stepper_layout(
    step3_state="active",
    show_background=False,
    content=[
        html.Div(
            html.Div(
                "Edit criteria ranges and weights:",
                className="col-lg-12 section-header first-header",
            ),
            className="row",
        ),
        html.Div(
            className="row block-row",
            id="criteria-edit-card",
        ),
        html.Div(
            [
                html.A(
                    html.Button(
                        "Previous",
                        className="btn btn-primary me-1",
                    ),
                    href="/upload",
                ),
                html.A(
                    html.Button(
                        "Next",
                        id="criteria-submit-btn",
                        className="btn btn-primary",
                        disabled=True,
                    ),
                    href="/dashboard",
                ),
            ],
            className="stepper-form-controls",
        ),
        dcc.Store(id="temp-params-store", storage_type="memory"),
    ],
)


@callback(
    Output("criteria-edit-card", "children"),
    Output("criteria-submit-btn", "disabled"),
    Input("data-store", "data"),
    State("data-filename-store", "data"),
    Input("params-store", "data"),
)
def update_params(data, data_filename, params):
    if data is None and data_filename is None:
        return (
            html.Div(
                html.I("Missing data. Go to previous step."),
                className="col-lg-12 block-row",
            ),
            True,
        )
    else:
        df = pd.DataFrame.from_dict(data)

        if params is None:
            params_dict = create_default_params_dict(df)
        else:
            params_dict = params

        criteria_table = create_criteria_table(params_dict)

        return criteria_table, False


@callback(
    Output({"type": "weight", "index": MATCH}, "style"),
    Output({"type": "expert_min", "index": MATCH}, "style"),
    Output({"type": "expert_max", "index": MATCH}, "style"),
    Output({"type": "objective", "index": MATCH}, "style"),
    Input({"type": "id_column", "index": MATCH}, "on"),
)
def check_id_switch(is_on):
    if is_on:
        return INVISIBLE, INVISIBLE, INVISIBLE, INVISIBLE
    else:
        return NO_STYLE, NO_STYLE, NO_STYLE, NO_STYLE


@callback(
    Output("temp-params-store", "data"),
    Input({"type": "criterion", "index": ALL}, "children"),
    Input({"type": "id_column", "index": ALL}, "on"),
    Input({"type": "weight", "index": ALL}, "value"),
    Input({"type": "expert_min", "index": ALL}, "value"),
    Input({"type": "expert_max", "index": ALL}, "value"),
    Input({"type": "objective", "index": ALL}, "value"),
)
def update_params_dict(criteria, id_column, weight, expert_min, expert_max, objective):
    temp_params_dict = dict()

    for i, criterion in enumerate(criteria):
        temp_params_dict[criterion] = {
            "id_column": "true" if id_column[i] else "false",
            "weight": weight[i],
            "expert_min": expert_min[i],
            "expert_max": expert_max[i],
            "objective": "max" if objective[i] else "min",
        }

    return temp_params_dict


@callback(
    Output("params-store", "data", allow_duplicate=True),
    Output("params-filename-store", "data", allow_duplicate=True),
    Input("criteria-submit-btn", "n_clicks"),
    State("temp-params-store", "data"),
    State("data-filename-store", "data"),
    prevent_initial_call="initial_duplicate",
)
def submit_criteria(n, params_dict, data_filename):
    if n is None:
        return no_update
    else:
        json_filename = data_filename.split(".")[0] + "_edited_settings.json"
        return params_dict, json_filename
