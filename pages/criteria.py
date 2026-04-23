import pandas as pd
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, no_update, callback
from dash.dependencies import Input, Output, State, MATCH, ALL

from common.data_functions import (
    AGGREGATION_METHOD_KEY,
    AGGREGATION_METHOD_LABELS,
    DEFAULT_AGGREGATION_METHOD,
    create_default_params_dict,
    get_aggregation_method,
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
            [
                html.Div(
                    [
                        dbc.Label("Ranking method", html_for="criteria-aggregation-method"),
                        dbc.Select(
                            id="criteria-aggregation-method",
                            options=[
                                {"label": label, "value": key}
                                for key, label in AGGREGATION_METHOD_LABELS.items()
                            ],
                            value=DEFAULT_AGGREGATION_METHOD,
                        ),
                        html.Small(
                            "Choose the aggregation method before moving to the analysis step.",
                            className="text-muted",
                        ),
                    ],
                    className="col-lg-12",
                )
            ],
            className="row block-row",
            id="criteria-method-section",
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
                html.Button(
                    "Next",
                    id="criteria-submit-btn",
                    className="btn btn-primary",
                    disabled=True,
                ),
            ],
            className="stepper-form-controls",
        ),
        html.Div(
            id="criteria-validation-msg",
            className="text-danger mt-2",
        ),
        dcc.Store(id="temp-params-store", storage_type="memory"),
        dcc.Location(id="criteria-redirect", refresh=True),
    ],
)


@callback(
    Output("criteria-edit-card", "children"),
    Output("criteria-submit-btn", "disabled"),
    Output("criteria-aggregation-method", "value"),
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
            DEFAULT_AGGREGATION_METHOD,
        )
    else:
        df = pd.DataFrame.from_dict(data)

        if params is None:
            params_dict = create_default_params_dict(df)
        else:
            params_dict = params

        criteria_table = create_criteria_table(params_dict)
        aggregation_method = get_aggregation_method(params_dict)

        return criteria_table, False, aggregation_method


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
    Input("criteria-aggregation-method", "value"),
)
def update_params_dict(criteria, id_column, weight, expert_min, expert_max, objective, aggregation_method):
    temp_params_dict = dict()

    for i, criterion in enumerate(criteria):
        temp_params_dict[criterion] = {
            "id_column": "true" if id_column[i] else "false",
            "weight": weight[i],
            "expert_min": expert_min[i],
            "expert_max": expert_max[i],
            "objective": "max" if objective[i] else "min",
        }

    temp_params_dict[AGGREGATION_METHOD_KEY] = aggregation_method or DEFAULT_AGGREGATION_METHOD
    return temp_params_dict


@callback(
    Output("criteria-submit-btn", "disabled", allow_duplicate=True),
    Output("criteria-validation-msg", "children"),
    Input("temp-params-store", "data"),
    prevent_initial_call=True,
)
def validate_criteria(temp_params):
    if not temp_params:
        return True, ""

    positive_weight = False
    range_errors = []
    for name, cfg in temp_params.items():
        if not isinstance(cfg, dict):
            continue
        if (cfg.get("id_column") or "false") == "true":
            continue
        try:
            w = float(cfg.get("weight") or 0)
        except (TypeError, ValueError):
            w = 0
        if w > 0:
            positive_weight = True
        try:
            lo = float(cfg.get("expert_min"))
            hi = float(cfg.get("expert_max"))
            if lo >= hi:
                range_errors.append(name)
        except (TypeError, ValueError):
            range_errors.append(name)

    messages = []
    if not positive_weight:
        messages.append(
            "At least one non-ID criterion must have a positive weight."
        )
    if range_errors:
        messages.append(
            "Invalid expert range (min must be < max) for: "
            + ", ".join(range_errors)
        )

    disabled = bool(messages)
    return disabled, " ".join(messages)


@callback(
    Output("params-store", "data", allow_duplicate=True),
    Output("params-filename-store", "data", allow_duplicate=True),
    Output("aggregation-method-store", "data", allow_duplicate=True),
    Output("criteria-redirect", "pathname"),
    Input("criteria-submit-btn", "n_clicks"),
    State("temp-params-store", "data"),
    State("data-filename-store", "data"),
    prevent_initial_call="initial_duplicate",
)
def submit_criteria(n, params_dict, data_filename):
    if n is None:
        return no_update, no_update, no_update, no_update
    else:
        json_filename = data_filename.split(".")[0] + "_edited_settings.json"
        return (
            params_dict,
            json_filename,
            get_aggregation_method(params_dict),
            "/dashboard",
        )
