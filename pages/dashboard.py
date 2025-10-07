import json
import dash
from dash import html, dcc, callback
from dash.dependencies import Input, Output, State, MATCH
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pandas.api.types import is_numeric_dtype

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
DEFAULT_EPSILON = 1e-6
POSTFACTUM_METHODS = {
    "improvement_single_feature": {
        "label": "Direct method (single criterion)",
        "description": "Modify a single criterion to surpass the target alternative.",
    },
    "improvement_features": {
        "label": "Lexicographic search (multiple criteria)",
        "description": "Iteratively adjust a subset of criteria using binary search.",
    },
    "improvement_non_linear_programming": {
        "label": "Non-linear programming",
        "description": "Solve an exact optimization model for the selected criteria subset.",
    },
    "improvement_genetic": {
        "label": "Evolutionary search (NSGA-II)",
        "description": "Explore the search space with a genetic algorithm to find Pareto-efficient improvements.",
    },
}
EXCLUDED_CRITERIA_COLUMNS = {
    "Rank",
    "WM",
    "WSD",
    "TOPSIS Score [R(v)]",
}
RESULT_DISPLAY_THRESHOLD = 1e-9
DEFAULT_SOLUTIONS_TO_DISPLAY = 5


def get_criteria_columns(df):
    if df is None:
        return []

    return [
        col
        for col in df.columns
        if col not in EXCLUDED_CRITERIA_COLUMNS and is_numeric_dtype(df[col])
    ]


def build_card_context(df):
    if df is None:
        return {"records": [], "index_columns": [], "criteria_columns": []}

    reset_df = df.reset_index()
    data_columns = set(df.columns)
    index_columns = [col for col in reset_df.columns if col not in data_columns]

    if not index_columns:
        # The original index had no name; Dash DataTable will expose it as "index"
        index_columns = ["Alternative"]
        reset_df = reset_df.rename(columns={"index": "Alternative"})

    return {
        "records": reset_df.to_dict("records"),
        "index_columns": index_columns,
        "criteria_columns": get_criteria_columns(df),
    }


def coerce_key_value(value):
    if isinstance(value, np.generic):
        return value.item()
    return value


def extract_alternative_key_label(record, index_columns):
    if record is None:
        return None, ""

    if not index_columns:
        raw_value = record.get("index")
        coerced = coerce_key_value(raw_value)
        label = str(coerced) if coerced not in (None, "") else "(Unnamed alternative)"
        return coerced, label

    values = [coerce_key_value(record.get(column)) for column in index_columns]
    key = values[0] if len(values) == 1 else tuple(values)
    label_parts = [str(v) for v in values if v not in (None, "")]
    label = " / ".join(label_parts) if label_parts else "(Unnamed alternative)"
    return key, label


def load_postfactum_runtime(query_param, store_data, params_dict):
    df = None
    params = params_dict

    if query_param == "playground":
        df = pd.read_csv("data/students.csv")
        with open("data/students_settings.json") as f:
            params = json.load(f)
    elif store_data is not None:
        df = pd.DataFrame.from_dict(store_data)

    if df is None or params is None:
        return None, None, None, None

    decision_df, expert_ranges, weights, objectives = prepare_wmsd_data(
        df.copy(), params
    )
    transformer = wmsdt.WMSDTransformer(wmsdt.RTOPSIS, server_setup.SOLVER)
    normalized_df = transformer.fit_transform(
        decision_df.copy(), weights, objectives, expert_ranges
    )

    ranked_df = df.copy()
    ranked_df.loc[:, "WM"] = normalized_df.loc[:, "Mean"].values
    ranked_df.loc[:, "WSD"] = normalized_df.loc[:, "Std"].values
    ranked_df.loc[:, "TOPSIS Score [R(v)]"] = normalized_df.loc[:, "R"].values
    ranked_df = ranked_df.sort_values("TOPSIS Score [R(v)]", ascending=False)
    ranked_df.insert(0, "Rank", range(1, ranked_df.shape[0] + 1))

    return transformer, decision_df, ranked_df, normalized_df


def build_postfactum_results_layout(
    method_key,
    result,
    transformer,
    decision_df,
    ranked_df,
    source_key,
    source_label,
    source_rank,
    target_key,
    target_label,
    target_rank,
    precision,
    solutions_to_display,
):
    if method_key not in POSTFACTUM_METHODS:
        return dbc.Alert("Unknown postfactum method.", color="danger")

    if result is None:
        return dbc.Alert(
            "No feasible improvement was found for the selected configuration.",
            color="warning",
        )

    metadata = None
    result_df = result
    if isinstance(result, tuple):
        result_df, metadata = result

    if result_df is None:
        return dbc.Alert(
            "No feasible improvement was found for the selected configuration.",
            color="warning",
        )

    if isinstance(result_df, pd.Series):
        result_df = result_df.to_frame().T
    elif not isinstance(result_df, pd.DataFrame):
        result_df = pd.DataFrame(result_df)

    if result_df.empty:
        return dbc.Alert(
            "The method returned an empty result set.",
            color="warning",
        )

    precision = precision if precision is not None else DEFAULT_PRECISION
    precision = int(precision)

    criteria_columns = decision_df.columns.tolist()
    agg_label = "TOPSIS Score [R(v)]"
    current_score = ranked_df.loc[source_key, agg_label]
    target_score = ranked_df.loc[target_key, agg_label]

    if solutions_to_display is None:
        solutions_to_display = DEFAULT_SOLUTIONS_TO_DISPLAY
    try:
        solutions_to_display = int(solutions_to_display)
    except (TypeError, ValueError):
        solutions_to_display = DEFAULT_SOLUTIONS_TO_DISPLAY
    solutions_to_display = max(1, solutions_to_display)
    solutions_count = min(len(result_df), solutions_to_display)

    def create_solution_component(position, solution_series):
        modifications = (
            solution_series.reindex(criteria_columns).fillna(0.0).astype(float)
        )

        original_series = decision_df.loc[source_key]
        if isinstance(original_series, pd.DataFrame):
            original_series = original_series.iloc[0]

        original_values = original_series.reindex(criteria_columns).astype(float)
        new_values = original_values + modifications

        modified_row = new_values.to_frame().T
        transformed_row = transformer.transform(modified_row)
        agg_letter = str(transformer.agg_fn.letter)
        new_score = transformed_row[agg_letter].iloc[0]
        new_mean = transformed_row["Mean"].iloc[0]
        new_std = transformed_row["Std"].iloc[0]

        updated_scores = ranked_df[agg_label].copy()
        updated_scores.loc[source_key] = new_score
        new_rank = (
            updated_scores.sort_values(ascending=False).index.get_loc(source_key) + 1
        )

        summary_items = [
            html.Li(
                f"Current R(v): {current_score:.{precision}f} → {new_score:.{precision}f}"
            ),
            html.Li(f"Target R(v): {target_score:.{precision}f} (rank {target_rank})"),
            html.Li(
                f"Weighted mean / std: {new_mean:.{precision}f} / {new_std:.{precision}f}"
            ),
            html.Li(f"Estimated new rank: {new_rank}"),
        ]

        changes_table = pd.DataFrame(
            {
                "Criterion": criteria_columns,
                "Original": original_values.values,
                "Change": modifications.values,
                "New value": new_values.values,
            }
        )

        mask = changes_table["Change"].abs() >= RESULT_DISPLAY_THRESHOLD
        if not mask.any():
            mask = changes_table["Change"].abs() == changes_table["Change"].abs().max()
        changes_table = changes_table[mask]

        table_component = styled_datatable(
            changes_table,
            precision=precision,
            row_selectable=False,
        )

        return dbc.AccordionItem(
            [
                html.P(
                    "Suggested modifications:",
                    className="fw-bold",
                ),
                table_component,
                html.P("Summary:", className="fw-bold mt-3"),
                html.Ul(summary_items),
            ],
            title=f"Solution #{position}",
        )

    accordion_items = [
        create_solution_component(idx + 1, result_df.iloc[idx])
        for idx in range(solutions_count)
    ]

    body = [
        html.H5(POSTFACTUM_METHODS[method_key]["label"], className="mb-3"),
        html.P(
            f"Improving {source_label} (rank {source_rank}) towards {target_label} (rank {target_rank})."
        ),
        dbc.Accordion(accordion_items, always_open=True),
    ]

    if metadata is not None:
        body.append(
            html.Div(
                html.Small(
                    "Genetic algorithm checkpoints were generated during the run.",
                    className="text-muted",
                )
            )
        )

    return html.Div(body, className="postfactum-results")


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
                    dcc.Store(id="wmsd-data-store", storage_type="memory"),
                    dcc.Store(id="highlight-color-store", storage_type="local"),
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
    card_context = build_card_context(df)

    return html.Div(
        children=[
            dcc.Store(
                id={"type": "postfactum-card-context", "index": id},
                data=card_context,
                storage_type="memory",
            ),
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
                        dbc.Tab(
                            postfactum_method_tab(id, df),
                            label="Method and options",
                        ),
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
                    styled_datatable(
                        df,
                        precision,
                        row_selectable="single",
                        id={"type": "postfactum-source-table", "index": id},
                    ),
                    className="col-md-6",
                ),
                html.Div(
                    styled_datatable(
                        df,
                        precision,
                        row_selectable="single",
                        id={"type": "postfactum-target-table", "index": id},
                    ),
                    className="col-md-6",
                ),
            ]
        ),
    ]


def postfactum_method_tab(id, df):
    criteria_columns = get_criteria_columns(df)
    criteria_options = [
        {"label": criterion, "value": criterion} for criterion in criteria_columns
    ]

    default_single_feature = (
        criteria_options[0]["value"] if len(criteria_options) > 0 else None
    )
    default_multi_features = [option["value"] for option in criteria_options[:2]]

    epsilon_input = dbc.Input(
        id={"type": "postfactum-epsilon", "index": id},
        type="number",
        value=DEFAULT_EPSILON,
        step=1e-6,
        min=0,
        max=0.5,
        debounce=True,
        className="form-control",
    )

    return html.Div(
        [
            dbc.Row(
                [
                    html.P(
                        "Select the improvement method and configure its parameters. The wizard "
                        "will use the current ranking to compute the required changes.",
                        className="text-muted",
                    )
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("Improvement method"),
                            dbc.RadioItems(
                                id={"type": "postfactum-method-choice", "index": id},
                                options=[
                                    {
                                        "label": POSTFACTUM_METHODS[key]["label"],
                                        "value": key,
                                    }
                                    for key in POSTFACTUM_METHODS
                                ],
                                value="improvement_single_feature",
                                inputClassName="me-2",
                                labelClassName="d-block",
                            ),
                        ],
                        md=6,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Numerical precision (epsilon)"),
                            epsilon_input,
                            html.Small(
                                "Smaller values increase accuracy but may prolong computation.",
                                className="text-muted",
                            ),
                            html.Hr(),
                            dbc.Alert(
                                "Select the source and target alternatives to enable the analysis.",
                                color="info",
                                id={
                                    "type": "postfactum-selection-summary",
                                    "index": id,
                                },
                                className="py-2",
                            ),
                        ],
                        md=6,
                    ),
                ]
            ),
            html.Hr(),
            html.Div(
                [
                    html.H5("Method-specific options", className="section-h5"),
                    html.Div(
                        [
                            dbc.Label("Criterion to modify"),
                            dbc.Select(
                                id={
                                    "type": "postfactum-single-feature-criterion",
                                    "index": id,
                                },
                                options=criteria_options,
                                value=default_single_feature,
                            ),
                        ],
                        id={
                            "type": "postfactum-single-feature-options",
                            "index": id,
                        },
                    ),
                    html.Div(
                        [
                            dbc.Label("Criteria subset (ordered)"),
                            dcc.Dropdown(
                                id={
                                    "type": "postfactum-features-dropdown",
                                    "index": id,
                                },
                                options=criteria_options,
                                value=default_multi_features,
                                multi=True,
                                clearable=False,
                            ),
                        ],
                        id={
                            "type": "postfactum-multi-feature-options",
                            "index": id,
                        },
                        style={"display": "none"},
                    ),
                    html.Div(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            dbc.Label(
                                                "Criteria subset for optimization"
                                            ),
                                            dcc.Dropdown(
                                                id={
                                                    "type": "postfactum-nlp-features",
                                                    "index": id,
                                                },
                                                options=criteria_options,
                                                value=default_multi_features,
                                                multi=True,
                                                clearable=False,
                                            ),
                                        ],
                                        md=8,
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Label("Constraints"),
                                            dbc.Switch(
                                                id={
                                                    "type": "postfactum-constant-wm",
                                                    "index": id,
                                                },
                                                value=False,
                                                label="Keep weighted mean constant",
                                            ),
                                        ],
                                        md=4,
                                        className="d-flex align-items-end",
                                    ),
                                ]
                            ),
                        ],
                        id={
                            "type": "postfactum-nlp-options",
                            "index": id,
                        },
                        style={"display": "none"},
                    ),
                    html.Div(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            dbc.Label("Criteria subset for evolution"),
                                            dcc.Dropdown(
                                                id={
                                                    "type": "postfactum-genetic-features",
                                                    "index": id,
                                                },
                                                options=criteria_options,
                                                value=default_multi_features,
                                                multi=True,
                                                clearable=False,
                                            ),
                                        ],
                                        md=7,
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Label("Population size"),
                                            dbc.Input(
                                                id={
                                                    "type": "postfactum-popsize",
                                                    "index": id,
                                                },
                                                type="number",
                                                min=50,
                                                step=50,
                                                value=None,
                                            ),
                                        ],
                                        md=3,
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Label("Generations"),
                                            dbc.Input(
                                                id={
                                                    "type": "postfactum-generations",
                                                    "index": id,
                                                },
                                                type="number",
                                                min=50,
                                                step=50,
                                                value=200,
                                            ),
                                        ],
                                        md=2,
                                    ),
                                ]
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            dbc.Switch(
                                                id={
                                                    "type": "postfactum-allow-deterioration",
                                                    "index": id,
                                                },
                                                value=False,
                                                label="Allow temporary deterioration",
                                            ),
                                            dbc.InputGroup(
                                                [
                                                    dbc.InputGroupText(
                                                        "Solutions to display"
                                                    ),
                                                    dbc.Input(
                                                        id={
                                                            "type": "postfactum-solutions",
                                                            "index": id,
                                                        },
                                                        type="number",
                                                        min=1,
                                                        max=20,
                                                        step=1,
                                                        value=DEFAULT_SOLUTIONS_TO_DISPLAY,
                                                    ),
                                                ]
                                            ),
                                        ]
                                    )
                                ]
                            ),
                        ],
                        id={
                            "type": "postfactum-genetic-options",
                            "index": id,
                        },
                        style={"display": "none"},
                    ),
                ],
            ),
            html.Hr(),
            html.Div(
                [
                    dbc.Button(
                        [
                            html.I(className="fa-solid fa-play me-2"),
                            "Run analysis",
                        ],
                        color="primary",
                        id={"type": "postfactum-run-btn", "index": id},
                    )
                ],
                className="text-end",
            ),
        ]
    )


def postfactum_results_tab(id):
    return dcc.Loading(
        html.Div(
            dbc.Alert(
                "Run the analysis to preview suggested improvement actions.",
                color="secondary",
                className="py-2",
            ),
            id={"type": "postfactum-results-container", "index": id},
        ),
        type="default",
    )


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
                            dbc.Label("Choose the highlight circle outline color:"),
                            dbc.Input(
                                id="highlight-color-input",
                                value="#FFFFFF",
                                type="color",
                                className="form-control",
                                style={"width": "100px", "height": "40px"},
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
    df = None
    fig = None

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

    if df is not None and params_dict is not None:
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
    Output("wmsd-data-store", "data"),
    Output("highlight-color-input", "value"),
    Input("dashboard-query-param", "value"),
    Input("data-store", "data"),
    Input("data-filename-store", "data"),
    Input("params-store", "data"),
    Input("precision-store", "data"),
    Input("colorscale-store", "data"),
    Input("highlight-color-store", "data"),
)
def update_from_store(
    query_param,
    store_data,
    filename,
    params_dict,
    precision,
    colorscale,
    highlight_color,
):
    df, precision, colorscale, params_dict, fig = extract_data_from_store(
        query_param, store_data, params_dict, precision, colorscale, plot=True
    )

    if df is not None:
        table = styled_datatable(
            df, precision=precision, row_selectable="single", id="ranking-table"
        )
        # Store the dataframe for use in highlighting callback
        wmsd_data = df[["WM", "WSD", "TOPSIS Score [R(v)]"]].to_dict("records")

        # Set default highlight color if not set
        if highlight_color is None:
            highlight_color = "#FFFFFF"

        return fig, table, precision, colorscale, wmsd_data, highlight_color
    else:
        return (
            None,
            data_preview_default_message(),
            DEFAULT_PRECISION,
            DEFAULT_COLORSCALE,
            None,
            "#FFFFFF",
        )


@callback(
    Output("download-params", "data"),
    Input("download-params-btn", "n_clicks"),
    State("data-filename-store", "data"),
    State("params-store", "data"),
    prevent_initial_call=True,
)
def download_params_dict(n_clicks, data_filename, params_dict):
    if data_filename is None:
        if params_dict is None:
            with open("data/students_settings.json") as f:
                params_dict = json.load(f)
        json_filename = "playground_settings.json"
    else:
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
    Output("highlight-color-store", "data"),
    Input("apply-changes-btn", "n_clicks"),
    State("precision-input", "value"),
    State("colorscale-dropdown", "value"),
    State("highlight-color-input", "value"),
    prevent_initial_call=True,
)
def change_precision(n_clicks, precision, colorscale, highlight_color):
    if n_clicks is not None and n_clicks > 0:
        return precision, colorscale, highlight_color
    else:
        return dash.no_update, dash.no_update, dash.no_update


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

        if df is None or df.empty:
            return dash.no_update

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


@callback(
    Output("ranking-fig", "figure", allow_duplicate=True),
    Input("ranking-table", "selected_rows"),
    State("ranking-fig", "figure"),
    State("wmsd-data-store", "data"),
    State("highlight-color-store", "data"),
    prevent_initial_call=True,
)
def highlight_selected_point(selected_rows, current_fig, wmsd_data, highlight_color):
    """Highlight the selected row's point in the WMSD visualization."""
    if current_fig is None or wmsd_data is None:
        return dash.no_update

    # Use default color if not set
    if highlight_color is None:
        highlight_color = "#FFFFFF"

    # Remove any existing highlight traces
    fig_data = [
        trace for trace in current_fig["data"] if trace.get("name") != "Selected"
    ]

    # If a row is selected, add a highlight
    if selected_rows and len(selected_rows) > 0:
        selected_idx = selected_rows[0]

        # Get the coordinates of the selected point
        selected_point = wmsd_data[selected_idx]
        wm = selected_point["WM"]
        wsd = selected_point["WSD"]

        # Create a scatter trace for the highlight (circle outline with user-selected color)
        highlight_trace = {
            "type": "scatter",
            "x": [wm],
            "y": [wsd],
            "mode": "markers",
            "name": "Selected",
            "marker": {
                "size": 20,
                "color": "rgba(255, 255, 255, 0)",  # Transparent fill
                "line": {"color": highlight_color, "width": 3},
            },
            "showlegend": False,
            "hoverinfo": "skip",
        }
        fig_data.append(highlight_trace)

    # Update the figure
    current_fig["data"] = fig_data

    return current_fig


@callback(
    Output({"type": "postfactum-selection-summary", "index": MATCH}, "children"),
    Output({"type": "postfactum-selection-summary", "index": MATCH}, "color"),
    Input({"type": "postfactum-source-table", "index": MATCH}, "selected_rows"),
    Input({"type": "postfactum-target-table", "index": MATCH}, "selected_rows"),
    State({"type": "postfactum-card-context", "index": MATCH}, "data"),
)
def update_selection_summary(source_selection, target_selection, card_context):
    if card_context is None or not card_context.get("records"):
        return "Upload data to configure the analysis.", "warning"

    records = card_context.get("records", [])
    index_columns = card_context.get("index_columns", [])

    def resolve_selection(selection):
        if not selection:
            return None, None, None
        idx = selection[0]
        if idx is None or idx < 0 or idx >= len(records):
            return None, None, None
        record = records[idx]
        key, label = extract_alternative_key_label(record, index_columns)
        rank = record.get("Rank")
        return key, label, rank

    source_key, source_label, source_rank = resolve_selection(source_selection)
    target_key, target_label, target_rank = resolve_selection(target_selection)

    if source_key is None:
        return "Select the source alternative you want to improve.", "info"

    if target_key is None:
        return "Select the target alternative you want to surpass.", "info"

    if source_rank is None or target_rank is None:
        return (
            "Unable to determine ranks for the selected rows. Please verify your dataset.",
            "warning",
        )

    if source_rank <= target_rank:
        return (
            f"The source alternative '{source_label}' is already ranked #{source_rank},"
            f" which is not worse than the selected target '{target_label}' (#{target_rank}).",
            "warning",
        )

    message = (
        f"Improving '{source_label}' (rank #{source_rank}) to outperform '{target_label}'"
        f" (rank #{target_rank})."
    )
    return message, "success"


@callback(
    Output({"type": "postfactum-single-feature-options", "index": MATCH}, "style"),
    Output({"type": "postfactum-multi-feature-options", "index": MATCH}, "style"),
    Output({"type": "postfactum-nlp-options", "index": MATCH}, "style"),
    Output({"type": "postfactum-genetic-options", "index": MATCH}, "style"),
    Input({"type": "postfactum-method-choice", "index": MATCH}, "value"),
)
def toggle_method_options(selected_method):
    visible = {"display": "block"}
    hidden = {"display": "none"}

    return (
        visible if selected_method == "improvement_single_feature" else hidden,
        visible if selected_method == "improvement_features" else hidden,
        visible if selected_method == "improvement_non_linear_programming" else hidden,
        visible if selected_method == "improvement_genetic" else hidden,
    )


@callback(
    Output({"type": "postfactum-results-container", "index": MATCH}, "children"),
    Input({"type": "postfactum-run-btn", "index": MATCH}, "n_clicks"),
    State({"type": "postfactum-method-choice", "index": MATCH}, "value"),
    State({"type": "postfactum-epsilon", "index": MATCH}, "value"),
    State({"type": "postfactum-single-feature-criterion", "index": MATCH}, "value"),
    State({"type": "postfactum-features-dropdown", "index": MATCH}, "value"),
    State({"type": "postfactum-nlp-features", "index": MATCH}, "value"),
    State({"type": "postfactum-constant-wm", "index": MATCH}, "value"),
    State({"type": "postfactum-genetic-features", "index": MATCH}, "value"),
    State({"type": "postfactum-popsize", "index": MATCH}, "value"),
    State({"type": "postfactum-generations", "index": MATCH}, "value"),
    State({"type": "postfactum-allow-deterioration", "index": MATCH}, "value"),
    State({"type": "postfactum-solutions", "index": MATCH}, "value"),
    State({"type": "postfactum-source-table", "index": MATCH}, "selected_rows"),
    State({"type": "postfactum-target-table", "index": MATCH}, "selected_rows"),
    State({"type": "postfactum-card-context", "index": MATCH}, "data"),
    State("dashboard-query-param", "value"),
    State("data-store", "data"),
    State("params-store", "data"),
    State("precision-store", "data"),
    prevent_initial_call=True,
)
def execute_postfactum_analysis(
    n_clicks,
    method_key,
    epsilon,
    single_feature,
    features_selection,
    nlp_features,
    constant_wm,
    genetic_features,
    popsize,
    n_generations,
    allow_deterioration,
    solutions_to_display,
    source_selection,
    target_selection,
    card_context,
    query_param,
    store_data,
    params_dict,
    precision,
):
    if not n_clicks:
        return dash.no_update

    if card_context is None or not card_context.get("records"):
        return dbc.Alert(
            "No dataset available. Upload data before running analyses.",
            color="warning",
        )

    if method_key not in POSTFACTUM_METHODS:
        return dbc.Alert("Please select a valid improvement method.", color="warning")

    records = card_context.get("records", [])
    index_columns = card_context.get("index_columns", [])

    def resolve(selection):
        if not selection:
            return None, None, None
        idx = selection[0]
        if idx is None or idx < 0 or idx >= len(records):
            return None, None, None
        record = records[idx]
        key, label = extract_alternative_key_label(record, index_columns)
        rank = record.get("Rank")
        return key, label, rank

    source_key, source_label, source_rank = resolve(source_selection)
    target_key, target_label, target_rank = resolve(target_selection)

    if source_key is None or target_key is None:
        return dbc.Alert(
            "Select both the source and the target alternatives before running the analysis.",
            color="info",
        )

    if source_rank is None or target_rank is None:
        return dbc.Alert(
            "Unable to determine ranks for the selected alternatives. Please verify your data.",
            color="warning",
        )

    if source_rank <= target_rank:
        return dbc.Alert(
            "The chosen source alternative is already ranked equal to or higher than the target.",
            color="warning",
        )

    epsilon = float(epsilon) if epsilon not in (None, "") else DEFAULT_EPSILON
    epsilon = max(1e-8, min(0.5, epsilon))

    transformer, decision_df, ranked_df, _ = load_postfactum_runtime(
        query_param, store_data, params_dict
    )

    if transformer is None or decision_df is None or ranked_df is None:
        return dbc.Alert(
            "Postfactum engine is unavailable. Upload data and settings first.",
            color="warning",
        )

    try:
        ranked_df.loc[source_key]
        ranked_df.loc[target_key]
    except KeyError:
        return dbc.Alert(
            "Selected alternatives are no longer present in the current ranking. Refresh the card.",
            color="warning",
        )

    method_kwargs = {}
    criteria_columns = decision_df.columns.tolist()

    if method_key == "improvement_single_feature":
        if not single_feature:
            return dbc.Alert("Choose a criterion to modify.", color="info")
        if single_feature not in criteria_columns:
            return dbc.Alert(
                "Selected criterion is not available in the dataset.", color="warning"
            )
        method_kwargs["feature_to_change"] = single_feature
    elif method_key == "improvement_features":
        features = features_selection or []
        if len(features) == 0:
            return dbc.Alert(
                "Select at least one criterion for the lexicographic search.",
                color="info",
            )
        if not set(features).issubset(criteria_columns):
            return dbc.Alert(
                "One or more selected criteria are invalid.", color="warning"
            )
        method_kwargs["features_to_change"] = features
    elif method_key == "improvement_non_linear_programming":
        features = nlp_features or []
        if len(features) == 0:
            return dbc.Alert(
                "Select at least one criterion for the non-linear programming solver.",
                color="info",
            )
        if not set(features).issubset(criteria_columns):
            return dbc.Alert(
                "One or more selected criteria are invalid.", color="warning"
            )
        method_kwargs["features_to_change"] = features
        method_kwargs["constant_WM"] = bool(constant_wm)
    elif method_key == "improvement_genetic":
        features = genetic_features or []
        if len(features) == 0:
            return dbc.Alert(
                "Select at least one criterion for the evolutionary search.",
                color="info",
            )
        if not set(features).issubset(criteria_columns):
            return dbc.Alert(
                "One or more selected criteria are invalid.", color="warning"
            )
        method_kwargs["features_to_change"] = features
        method_kwargs["allow_deterioration"] = bool(allow_deterioration)
        if popsize:
            method_kwargs["popsize"] = int(popsize)
        if n_generations:
            method_kwargs["n_generations"] = int(n_generations)
    else:
        return dbc.Alert("Unsupported method.", color="warning")

    try:
        result = transformer.improvement(
            method_key,
            int(source_rank),
            int(target_rank),
            epsilon,
            **method_kwargs,
        )
    except ValueError as exc:
        return dbc.Alert(str(exc), color="danger")
    except Exception as exc:  # pylint: disable=broad-except
        return dbc.Alert(
            f"The analysis failed: {exc}",
            color="danger",
        )

    try:
        layout = build_postfactum_results_layout(
            method_key,
            result,
            transformer,
            decision_df,
            ranked_df,
            source_key,
            source_label,
            int(source_rank),
            target_key,
            target_label,
            int(target_rank),
            precision,
            solutions_to_display,
        )
    except Exception as exc:  # pylint: disable=broad-except
        return dbc.Alert(
            f"Unable to build the results view: {exc}",
            color="danger",
        )

    return layout
