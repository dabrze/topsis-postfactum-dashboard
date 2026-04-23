import json
import dash
from dash import html, dcc, callback
from dash.dependencies import ALL, Input, Output, State, MATCH
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
    "improvement_mean": {
        "label": "Shift weighted mean",
        "description": "Find minimal change in the weighted mean; results are sampled inverse US-space solutions.",
    },
    "improvement_std": {
        "label": "Shift weighted std",
        "description": "Find minimal change in the weighted std; results are sampled inverse US-space solutions.",
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


def build_card_context(df, params_dict=None):
    if df is None:
        return {
            "records": [],
            "index_columns": [],
            "criteria_columns": [],
            "criteria_bounds": {},
        }

    # If the params dict declares id columns but they are still regular columns
    # in df (typical for the DataFrame produced by extract_data_from_store),
    # promote them to the index so the keys produced here match the keys that
    # prepare_wmsd_data uses downstream when building the transformer.
    if isinstance(params_dict, dict):
        declared_ids = [
            col
            for col, cfg in params_dict.items()
            if isinstance(cfg, dict)
            and (cfg.get("id_column") or "false") == "true"
            and col in df.columns
        ]
        if declared_ids:
            df = df.set_index(declared_ids)

    reset_df = df.reset_index()
    data_columns = set(df.columns)
    index_columns = [col for col in reset_df.columns if col not in data_columns]

    if not index_columns:
        # The original index had no name; Dash DataTable will expose it as "index"
        index_columns = ["Alternative"]
        reset_df = reset_df.rename(columns={"index": "Alternative"})

    criteria_columns = get_criteria_columns(df)

    # Capture per-criterion expert min/max from the params dict (if available),
    # falling back to observed min/max. These are used as UI defaults for the
    # per-criterion boundary-value inputs.
    criteria_bounds = {}
    for col in criteria_columns:
        col_min = None
        col_max = None
        if isinstance(params_dict, dict) and col in params_dict:
            entry = params_dict[col]
            col_min = entry.get("expert_min")
            col_max = entry.get("expert_max")
        if col_min is None:
            col_min = float(df[col].min())
        if col_max is None:
            col_max = float(df[col].max())
        criteria_bounds[col] = {"min": float(col_min), "max": float(col_max)}

    return {
        "records": reset_df.to_dict("records"),
        "index_columns": index_columns,
        "criteria_columns": criteria_columns,
        "criteria_bounds": criteria_bounds,
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

    # Align ranked_df's index with decision_df / transformer.X so downstream
    # lookups (ranked_df.loc[source_key]) work. prepare_wmsd_data promotes the
    # declared id columns to the DataFrame index, so mirror that here.
    id_columns = [
        col
        for col, cfg in params.items()
        if isinstance(cfg, dict)
        and (cfg.get("id_column") or "false") == "true"
        and col in df.columns
    ]
    ranked_df = df.copy()
    if id_columns:
        ranked_df = ranked_df.set_index(id_columns)
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
    colorscale=None,
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

    # Prime the WMSD background figure (cached on the transformer) so that
    # plot_improvement can overlay the trajectory arrow without rebuilding
    # the heatmap for every solution.
    plot_background_ready = True
    if getattr(transformer, "plot_background", None) is None:
        try:
            transformer.plot(
                plot_name="",
                color=colorscale or DEFAULT_COLORSCALE,
            )
        except Exception:  # pylint: disable=broad-except
            plot_background_ready = False

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
        # Use competition ranking (1 + number of strictly higher scores) so
        # that exact ties share the higher rank instead of being pushed below
        # by pandas' stable sort. Any numerical margin required to strictly
        # overcome the target is the solver's responsibility — we do not add
        # slack here.
        new_rank = int((updated_scores > new_score).sum()) + 1

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

        accordion_children = [
            html.P(
                "Suggested modifications:",
                className="fw-bold",
            ),
            table_component,
            html.P("Summary:", className="fw-bold mt-3"),
            html.Ul(summary_items),
        ]

        if plot_background_ready:
            try:
                changes_df = modifications.to_frame().T
                changes_df.index = [source_key]
                trajectory_fig = transformer.plot_improvement(
                    source_key, changes_df, show_names=False, change_number=0
                )
                accordion_children.extend(
                    [
                        html.P(
                            "Improvement trajectory in WMSD space:",
                            className="fw-bold mt-3",
                        ),
                        dcc.Graph(
                            figure=trajectory_fig,
                            config={"displayModeBar": False},
                            className="postfactum-trajectory-plot",
                        ),
                    ]
                )
            except Exception as exc:  # pylint: disable=broad-except
                accordion_children.append(
                    html.Small(
                        f"Could not render trajectory plot: {exc}",
                        className="text-muted",
                    )
                )

        return dbc.AccordionItem(
            accordion_children,
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


def postfactum_analysis_card(id, df, precision, colorscale, params_dict=None):
    card_context = build_card_context(df, params_dict)

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
                            html.Div(
                                id={
                                    "type": "postfactum-features-bounds",
                                    "index": id,
                                },
                                className="mt-2",
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
                                            html.Div(
                                                id={
                                                    "type": "postfactum-genetic-bounds",
                                                    "index": id,
                                                },
                                                className="mt-2",
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
                    html.Div(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            dbc.Label(
                                                "Number of inverse-US solutions"
                                            ),
                                            dbc.Input(
                                                id={
                                                    "type": "postfactum-mean-solutions",
                                                    "index": id,
                                                },
                                                type="number",
                                                min=1,
                                                max=20,
                                                step=1,
                                                value=DEFAULT_SOLUTIONS_TO_DISPLAY,
                                            ),
                                        ],
                                        md=4,
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Switch(
                                                id={
                                                    "type": "postfactum-allow-std",
                                                    "index": id,
                                                },
                                                value=False,
                                                label="Allow adjusting std if mean alone is insufficient",
                                            ),
                                        ],
                                        md=8,
                                        className="d-flex align-items-end",
                                    ),
                                ]
                            ),
                        ],
                        id={
                            "type": "postfactum-mean-options",
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
                                                "Number of inverse-US solutions"
                                            ),
                                            dbc.Input(
                                                id={
                                                    "type": "postfactum-std-solutions",
                                                    "index": id,
                                                },
                                                type="number",
                                                min=1,
                                                max=20,
                                                step=1,
                                                value=DEFAULT_SOLUTIONS_TO_DISPLAY,
                                            ),
                                        ],
                                        md=4,
                                    ),
                                ]
                            ),
                        ],
                        id={
                            "type": "postfactum-std-options",
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


def _component_to_html(component):
    """Best-effort conversion of a Dash component tree to an HTML string."""
    if component is None:
        return ""
    if isinstance(component, str):
        return component
    if isinstance(component, (int, float)):
        return str(component)
    if isinstance(component, list):
        return "".join(_component_to_html(c) for c in component)
    if isinstance(component, dict):
        ctype = component.get("type")
        props = component.get("props", {}) or {}
        children = props.get("children")
        inner = _component_to_html(children)
        tag_map = {
            "Div": "div",
            "P": "p",
            "Span": "span",
            "H1": "h1",
            "H2": "h2",
            "H3": "h3",
            "H4": "h4",
            "H5": "h5",
            "H6": "h6",
            "Ul": "ul",
            "Li": "li",
            "Small": "small",
            "Strong": "strong",
            "Em": "em",
            "Br": "br",
            "Hr": "hr",
            "Table": "table",
            "Thead": "thead",
            "Tbody": "tbody",
            "Tr": "tr",
            "Th": "th",
            "Td": "td",
            "I": "i",
        }
        tag = tag_map.get(ctype)
        if tag:
            cls = props.get("className", "")
            cls_attr = f' class="{cls}"' if cls else ""
            if tag in ("br", "hr"):
                return f"<{tag}/>"
            return f"<{tag}{cls_attr}>{inner}</{tag}>"
        if ctype == "Graph":
            fig = props.get("figure")
            if fig is not None:
                try:
                    go_fig = go.Figure(fig)
                    return go_fig.to_html(
                        full_html=False, include_plotlyjs=False
                    )
                except Exception:  # pylint: disable=broad-except
                    return ""
            return ""
        if ctype == "AccordionItem":
            title = props.get("title", "")
            return (
                f'<section class="report-accordion-item">'
                f"<h4>{title}</h4>{inner}</section>"
            )
        if ctype == "Accordion":
            return f'<div class="report-accordion">{inner}</div>'
        if ctype == "Alert":
            color = props.get("color", "info")
            return f'<div class="alert alert-{color}">{inner}</div>'
        if ctype == "DataTable":
            data = props.get("data") or []
            columns = props.get("columns") or []
            if not data or not columns:
                return ""
            header = "".join(f"<th>{c.get('name', c.get('id', ''))}</th>" for c in columns)
            rows_html = []
            for row in data:
                cells = "".join(
                    f"<td>{row.get(c.get('id'), '')}</td>" for c in columns
                )
                rows_html.append(f"<tr>{cells}</tr>")
            return (
                f'<table class="report-table"><thead><tr>{header}</tr></thead>'
                f'<tbody>{"".join(rows_html)}</tbody></table>'
            )
        # Fallback: render inner content if present
        return inner
    return ""


@callback(
    Output("download-report", "data"),
    Input("download-report-btn", "n_clicks"),
    State("data-filename-store", "data"),
    State("ranking-fig", "figure"),
    State("ranking-datatable", "children"),
    State({"type": "postfactum-analysis", "index": ALL}, "id"),
    State({"type": "postfactum-card-context", "index": ALL}, "data"),
    State({"type": "postfactum-results-container", "index": ALL}, "children"),
    prevent_initial_call=True,
)
def download_html_report(
    n_clicks,
    data_filename,
    ranking_fig,
    ranking_table,
    card_ids,
    card_contexts,
    results_children,
):
    if not n_clicks:
        return dash.no_update

    dataset_name = (
        data_filename.rsplit(".", 1)[0]
        if data_filename
        else "playground"
    )

    ranking_fig_html = ""
    if ranking_fig is not None:
        try:
            ranking_fig_html = go.Figure(ranking_fig).to_html(
                full_html=False, include_plotlyjs="cdn"
            )
        except Exception:  # pylint: disable=broad-except
            ranking_fig_html = ""

    ranking_table_html = _component_to_html(ranking_table)

    card_sections = []
    ordered = sorted(
        zip(card_ids or [], card_contexts or [], results_children or []),
        key=lambda triple: (triple[0] or {}).get("index", 0),
    )
    for cid, ctx, results in ordered:
        idx = (cid or {}).get("index", "?")
        results_html = _component_to_html(results) or (
            '<p class="text-muted">'
            "No analysis has been run yet for this card."
            "</p>"
        )
        card_sections.append(
            f'<section class="report-card">'
            f"<h3>Postfactum analysis #{idx}</h3>"
            f"{results_html}</section>"
        )
    cards_html = "".join(card_sections) or (
        '<p class="text-muted">No postfactum analyses were configured.</p>'
    )

    import datetime

    timestamp = datetime.datetime.now().isoformat(timespec="seconds")
    html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>TOPSIS Postfactum Report — {dataset_name}</title>
<style>
body {{ font-family: Arial, Helvetica, sans-serif; margin: 2rem; color: #222; }}
h1, h2, h3, h4 {{ color: #1f3b70; }}
table.report-table {{ border-collapse: collapse; margin: 0.5rem 0; }}
table.report-table th, table.report-table td {{
  border: 1px solid #ccc; padding: 4px 8px; font-size: 0.9rem;
}}
table.report-table thead {{ background: #eef; }}
section.report-card {{
  border: 1px solid #ddd; border-radius: 6px; padding: 1rem;
  margin: 1rem 0; background: #fafafa;
}}
section.report-accordion-item {{
  border-left: 3px solid #1f3b70; padding: 0.5rem 1rem; margin: 0.5rem 0;
  background: #fff;
}}
.text-muted {{ color: #888; }}
.alert {{ padding: 0.6rem; border-radius: 4px; margin: 0.5rem 0; }}
.alert-info {{ background: #e7f1ff; }}
.alert-warning {{ background: #fff3cd; }}
.alert-danger {{ background: #f8d7da; }}
</style>
</head>
<body>
<h1>TOPSIS Postfactum Report</h1>
<p><strong>Dataset:</strong> {dataset_name}<br/>
<strong>Generated:</strong> {timestamp}</p>

<h2>Ranking visualization</h2>
{ranking_fig_html or '<p class="text-muted">No ranking figure available.</p>'}

<h2>Ranking table</h2>
{ranking_table_html or '<p class="text-muted">No ranking table available.</p>'}

<h2>Postfactum analyses</h2>
{cards_html}
</body>
</html>
"""

    return dict(content=html_doc, filename=f"{dataset_name}_report.html")


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

        new_card = postfactum_analysis_card(
            n_clicks, df, precision, colorscale, params_dict
        )
        current_analyses.insert(-1, new_card)

        return current_analyses
    else:
        return dash.no_update


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
        return dash.no_update, dash.no_update


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
    Output({"type": "postfactum-mean-options", "index": MATCH}, "style"),
    Output({"type": "postfactum-std-options", "index": MATCH}, "style"),
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
        visible if selected_method == "improvement_mean" else hidden,
        visible if selected_method == "improvement_std" else hidden,
    )


def _build_boundary_inputs(container_type, card_id, selected_features, bounds_by_feature):
    """Builds a list of per-feature numeric inputs for boundary_values.

    Each input's id is of the form
    {"type": container_type + "-value", "index": card_id, "feature": <name>}.
    The "type" layout is chosen so pattern-matching callbacks can collect all
    inputs for a given card using ALL on the "feature" key.
    """
    if not selected_features:
        return [
            html.Small(
                "Select at least one criterion to configure its boundary.",
                className="text-muted",
            )
        ]

    value_type = container_type + "-value"
    rows = []
    for feature in selected_features:
        bounds = (bounds_by_feature or {}).get(feature, {})
        default_max = bounds.get("max")
        rows.append(
            dbc.Row(
                [
                    dbc.Col(html.Small(feature), md=5, className="pt-2"),
                    dbc.Col(
                        dbc.Input(
                            id={
                                "type": value_type,
                                "index": card_id,
                                "feature": feature,
                            },
                            type="number",
                            value=default_max,
                            placeholder="criterion max",
                            size="sm",
                        ),
                        md=7,
                    ),
                ],
                className="g-1 mb-1",
            )
        )
    return [
        html.Details(
            [
                html.Summary(
                    html.Small(
                        "Advanced: maximum allowable value per criterion",
                        className="text-muted",
                    )
                ),
                html.Div(rows, className="mt-2"),
            ],
            open=False,
        )
    ]


@callback(
    Output({"type": "postfactum-features-bounds", "index": MATCH}, "children"),
    Input({"type": "postfactum-features-dropdown", "index": MATCH}, "value"),
    State({"type": "postfactum-features-dropdown", "index": MATCH}, "id"),
    State({"type": "postfactum-card-context", "index": MATCH}, "data"),
)
def populate_features_bounds(selected_features, dropdown_id, card_context):
    card_id = dropdown_id["index"] if dropdown_id else None
    bounds = (card_context or {}).get("criteria_bounds", {}) if card_context else {}
    return _build_boundary_inputs(
        "postfactum-features-bound", card_id, selected_features or [], bounds
    )


@callback(
    Output({"type": "postfactum-genetic-bounds", "index": MATCH}, "children"),
    Input({"type": "postfactum-genetic-features", "index": MATCH}, "value"),
    State({"type": "postfactum-genetic-features", "index": MATCH}, "id"),
    State({"type": "postfactum-card-context", "index": MATCH}, "data"),
)
def populate_genetic_bounds(selected_features, dropdown_id, card_context):
    card_id = dropdown_id["index"] if dropdown_id else None
    bounds = (card_context or {}).get("criteria_bounds", {}) if card_context else {}
    return _build_boundary_inputs(
        "postfactum-genetic-bound", card_id, selected_features or [], bounds
    )


def _collect_boundary_values(selected_features, bound_ids, bound_values):
    """Given the ordered list of selected features and the pattern-matching
    State arrays for boundary inputs (ids + values), return a list of floats
    in the same order as `selected_features`, or None if every input is empty.
    """
    if not selected_features:
        return None

    by_feature = {}
    for entry_id, value in zip(bound_ids or [], bound_values or []):
        feature = entry_id.get("feature") if isinstance(entry_id, dict) else None
        if feature is not None:
            by_feature[feature] = value

    ordered = []
    any_value = False
    for feature in selected_features:
        raw = by_feature.get(feature)
        if raw in (None, ""):
            ordered.append(None)
        else:
            try:
                ordered.append(float(raw))
                any_value = True
            except (TypeError, ValueError):
                ordered.append(None)
    if not any_value:
        return None
    # If any entries are still None but others are set, the library requires
    # a complete list; we cannot supply a partial list, so signal the caller.
    if any(v is None for v in ordered):
        return "INCOMPLETE"
    return ordered


@callback(
    Output({"type": "postfactum-results-container", "index": MATCH}, "children"),
    Input({"type": "postfactum-run-btn", "index": MATCH}, "n_clicks"),
    State({"type": "postfactum-method-choice", "index": MATCH}, "value"),
    State({"type": "postfactum-epsilon", "index": MATCH}, "value"),
    State({"type": "postfactum-single-feature-criterion", "index": MATCH}, "value"),
    State({"type": "postfactum-features-dropdown", "index": MATCH}, "value"),
    State(
        {"type": "postfactum-features-bound-value", "index": MATCH, "feature": ALL},
        "id",
    ),
    State(
        {"type": "postfactum-features-bound-value", "index": MATCH, "feature": ALL},
        "value",
    ),
    State({"type": "postfactum-nlp-features", "index": MATCH}, "value"),
    State({"type": "postfactum-constant-wm", "index": MATCH}, "value"),
    State({"type": "postfactum-genetic-features", "index": MATCH}, "value"),
    State(
        {"type": "postfactum-genetic-bound-value", "index": MATCH, "feature": ALL},
        "id",
    ),
    State(
        {"type": "postfactum-genetic-bound-value", "index": MATCH, "feature": ALL},
        "value",
    ),
    State({"type": "postfactum-popsize", "index": MATCH}, "value"),
    State({"type": "postfactum-generations", "index": MATCH}, "value"),
    State({"type": "postfactum-allow-deterioration", "index": MATCH}, "value"),
    State({"type": "postfactum-solutions", "index": MATCH}, "value"),
    State({"type": "postfactum-mean-solutions", "index": MATCH}, "value"),
    State({"type": "postfactum-allow-std", "index": MATCH}, "value"),
    State({"type": "postfactum-std-solutions", "index": MATCH}, "value"),
    State({"type": "postfactum-source-table", "index": MATCH}, "selected_rows"),
    State({"type": "postfactum-target-table", "index": MATCH}, "selected_rows"),
    State({"type": "postfactum-card-context", "index": MATCH}, "data"),
    State("dashboard-query-param", "value"),
    State("data-store", "data"),
    State("params-store", "data"),
    State("precision-store", "data"),
    State("colorscale-store", "data"),
    background=True,
    running=[
        (
            Output({"type": "postfactum-run-btn", "index": MATCH}, "disabled"),
            True,
            False,
        ),
        (
            Output({"type": "postfactum-run-btn", "index": MATCH}, "children"),
            [
                dbc.Spinner(size="sm", color="light"),
                " Running analysis...",
            ],
            [
                html.I(className="fa-solid fa-play me-2"),
                "Run analysis",
            ],
        ),
    ],
    prevent_initial_call=True,
)
def execute_postfactum_analysis(
    n_clicks,
    method_key,
    epsilon,
    single_feature,
    features_selection,
    features_bound_ids,
    features_bound_values,
    nlp_features,
    constant_wm,
    genetic_features,
    genetic_bound_ids,
    genetic_bound_values,
    popsize,
    n_generations,
    allow_deterioration,
    solutions_to_display,
    mean_solutions,
    allow_std,
    std_solutions,
    source_selection,
    target_selection,
    card_context,
    query_param,
    store_data,
    params_dict,
    precision,
    colorscale,
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
        bounds = _collect_boundary_values(
            features, features_bound_ids, features_bound_values
        )
        if bounds == "INCOMPLETE":
            return dbc.Alert(
                "Boundary values must be specified for every selected criterion, "
                "or left blank for all of them.",
                color="warning",
            )
        if bounds is not None:
            method_kwargs["boundary_values"] = bounds
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
        bounds = _collect_boundary_values(
            features, genetic_bound_ids, genetic_bound_values
        )
        if bounds == "INCOMPLETE":
            return dbc.Alert(
                "Boundary values must be specified for every selected criterion, "
                "or left blank for all of them.",
                color="warning",
            )
        if bounds is not None:
            method_kwargs["boundary_values"] = bounds
        if popsize:
            method_kwargs["popsize"] = int(popsize)
        if n_generations:
            method_kwargs["n_generations"] = int(n_generations)
    elif method_key == "improvement_mean":
        method_kwargs["allow_std"] = bool(allow_std)
        try:
            method_kwargs["solutions_number"] = max(
                1, int(mean_solutions or DEFAULT_SOLUTIONS_TO_DISPLAY)
            )
        except (TypeError, ValueError):
            method_kwargs["solutions_number"] = DEFAULT_SOLUTIONS_TO_DISPLAY
    elif method_key == "improvement_std":
        try:
            method_kwargs["solutions_number"] = max(
                1, int(std_solutions or DEFAULT_SOLUTIONS_TO_DISPLAY)
            )
        except (TypeError, ValueError):
            method_kwargs["solutions_number"] = DEFAULT_SOLUTIONS_TO_DISPLAY
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
            colorscale,
        )
    except Exception as exc:  # pylint: disable=broad-except
        return dbc.Alert(
            f"Unable to build the results view: {exc}",
            color="danger",
        )

    return layout
