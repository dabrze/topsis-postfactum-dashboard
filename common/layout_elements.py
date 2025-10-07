import dash
import dash_bootstrap_components as dbc
from dash_dangerously_set_inner_html import DangerouslySetInnerHTML
from dash import html, dash_table, dcc
from dash.dash_table.Format import Format, Scheme
import dash_daq as daq

EXTERNAL_STYLESHEETS = [
    dbc.themes.BOOTSTRAP,
    "https://cdn.jsdelivr.net/npm/bs-stepper/dist/css/bs-stepper.min.css",
    "https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap",
    "https://fonts.googleapis.com/css2?family=Roboto+Mono&display=swap",
    "https://fonts.googleapis.com/css2?family=Raleway:wght@400&display=swap",
    dbc.icons.FONT_AWESOME,
]


EXTERNAL_SCRIPTS = [
    {
        "src": "https://code.jquery.com/jquery-3.4.1.min.js",
    },
    {
        "src": "https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js",
    },
    {
        "src": "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.min.js",
    },
]

NO_STYLE = {}
INVISIBLE = {"visibility": "hidden"}
SHOW = {"display": "block"}
HIDE = {"display": "none"}
OVERLAY_STYLE = {
    "visibility": "visible",
    "opacity": 0.5,
    "backgroundColor": "white",
}


def header(app):
    """
    Generates the header component for the dashboard.

    Parameters:
    - app (Dash): The Dash application object.

    Returns:
    - DangerouslySetInnerHTML: The generated header component.
    """
    return DangerouslySetInnerHTML(
        f"""
<nav id="header" class="container navbar-light navbar navbar-expand-sm">
    <div class="logo-container">
        <div id="main-navbar-header" class="navbar-header">
            <h1 id="header-panel">
                <a id="logo-anchor" href="/"><img id="main-logo" alt="Postfactum Analysis Dashboard logo"
                src="{app.get_asset_url("img/pad_logo.svg")}"> Postfactum Analysis Dashboard</a>
            </h1>
        </div>
    </div>
    <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav"
    aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse right" id="navbarNav">
    <ul class="navbar-nav ml-auto">
      <li class="nav-item">
        <a id="about-link" class="nav-link" href="/about/">About</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="javascript:void(0);" onclick="javascript:tour();">Tour</a>
      </li>
    </ul>
  </div></nav>"""
    )


def footer():
    """
    Generates the footer component for the dashboard.

    Returns:
    - html.Div: The generated footer component.
    """
    return html.Div(
        [
            DangerouslySetInnerHTML(
                """
    <div class="container">
        <div class="row">
            <div class="col-sm-5 col-xs-12">
                <h4>How it works</h4>
                <p>
                    Postfactum Analysis Dashboard is a tool for performing classic TOPSIS rankings
                    and analyzing the possiblities of improving the positions
                    of selected alternatives. It also uses WMSD visualizations to show the ranking
                    as a 2D plot. Upload your files to try it out!
                </p>
            </div>
            <div class="col-sm-3 col-xs-6">
                <h4>Contact</h4>
                <p>
                    Need help? Found a bug? Have comments? Want to collaborate?
                    <script type="text/javascript" language="javascript">
                    <!-- //
                    ML="omCdztsk/nilh>@\":brf<c!=.uep a";
                    MI="DML<BJCG?1M:;50@3MB:I64HAB4J4:967:>E6HKI5HK049M9HK;?=2095ME5LI6FD8M=";
                    OT="";
                    for(j=0;j<MI.length;j++){
                    OT+=ML.charAt(MI.charCodeAt(j)-48);
                    }document.write(OT);
                    // --></script><a href="mailto:dariusz.brzezinski@cs.put.poznan.pl">Contact us!</a>
                    <noscript>[Turn on JavaScript to see the email address]</noscript>
                </p>
            </div>
            <div class="col-sm-4 col-xs-6">
                <h4>Citing</h4>
                <p>
                    Susmaga <i>et al.</i> (2024)
                    Towards explainable TOPSIS: Visual insights into the effects of weights and aggregations
                    on rankings. <i>Applied Soft Computing</i>, 153, 111279.
                    <a target="_blank" rel="noopener" href="https://doi.org/10.1016/j.asoc.2024.111279"
                    onclick="gtag('event', 'follow', {'event_category': 'Actions'});">
                    <i class="fas fa-external-link-alt" title="Link to the CheckMyBlob publication"></i>
                    </a>
                </p>
            </div>
        </div>
    </div>
                                    """
            )
        ],
        id="footer",
    )


def stepper_layout(
    step1_state="",
    step2_state="",
    step3_state="",
    step4_state="",
    content="",
    show_background=True,
):
    """
    Generates the stepper layout component for the dashboard.

    Parameters:
    - step1_state (str): The state of step 1.
    - step2_state (str): The state of step 2.
    - step3_state (str): The state of step 3.
    - step4_state (str): The state of step 4.
    - content (str): The content of the stepper.

    Returns:
    - str: The generated stepper layout component.
    """
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                html.A(
                                    [
                                        html.Span("1", className="bs-stepper-circle"),
                                        html.Span(
                                            "Welcome", className="bs-stepper-label"
                                        ),
                                    ],
                                    className="step-trigger",
                                    href="/",
                                ),
                                className=f"step {step1_state}",
                            ),
                            html.Div(className="line"),
                            html.Div(
                                html.A(
                                    [
                                        html.Span("2", className="bs-stepper-circle"),
                                        html.Span(
                                            "Upload data", className="bs-stepper-label"
                                        ),
                                    ],
                                    className="step-trigger",
                                    href="/upload",
                                ),
                                className=f"step {step2_state}",
                            ),
                            html.Div(className="line"),
                            html.Div(
                                html.A(
                                    [
                                        html.Span("3", className="bs-stepper-circle"),
                                        html.Span(
                                            "Set criteria", className="bs-stepper-label"
                                        ),
                                    ],
                                    className="step-trigger",
                                    href="/criteria",
                                ),
                                className=f"step {step3_state}",
                            ),
                            html.Div(className="line"),
                            html.Div(
                                html.A(
                                    [
                                        html.Span("4", className="bs-stepper-circle"),
                                        html.Span(
                                            "Analyze", className="bs-stepper-label"
                                        ),
                                    ],
                                    className="step-trigger",
                                    href="/dashboard",
                                ),
                                className=f"step {step4_state}",
                            ),
                        ],
                        className="bs-stepper-header",
                    ),
                    html.Div(content, className="bs-stepper-content"),
                ],
                id="submit-stepper",
                className=f"bs-stepper vertical {'col-lg-8' if show_background else 'col-lg-12'} col-md-12",
            ),
            html.Div(
                html.Img(
                    id="pad-background",
                    className="img-fluid",
                    style={
                        "display": f"{'none' if not show_background else 'inherit'}"
                    },
                    src=dash.get_asset_url("img/pad_schematic.png"),
                    alt="Postfactum splash",
                ),
                className="col-lg-4 d-none d-lg-block",
            ),
        ],
        className="row",
    )


def styled_datatable(df, precision=3, row_selectable=False, id=None):
    columns = []

    for i, c in enumerate(df.columns):
        column_type = df.dtypes.iat[i]
        if column_type == "float64":
            columns.append(
                dict(
                    name=c,
                    id=c,
                    type="numeric",
                    format=Format(precision=precision, scheme=Scheme.fixed),
                )
            )
        elif column_type == "int64":
            columns.append(
                dict(name=c, id=c, type="numeric", format=Format().group(True))
            )
        else:
            columns.append(dict(name=c, id=c))

    # Build the DataTable kwargs, only including id if it's provided
    datatable_kwargs = {
        "data": df.to_dict("records"),
        "columns": columns,
        "editable": False,
        "row_selectable": row_selectable,
        "sort_action": "native",
        "page_action": "native",
        "page_size": 10,
        "style_as_list_view": True,
        "style_cell": {"padding": "5px"},
        "style_header": {"backgroundColor": "white", "fontWeight": "bold"},
        "style_table": {"overflowX": "auto"},
        "style_data_conditional": [
            {
                "if": {"row_index": "odd"},
                "backgroundColor": "rgb(240, 240, 240)",
            }
        ],
    }

    if id is not None:
        datatable_kwargs["id"] = id

    return dash_table.DataTable(**datatable_kwargs)


def upload_default_message():
    return [
        html.Br(),
        html.I(className="fa-solid fa-cloud-arrow-up"),
        " Drop file here or",
        html.Br(),
        "click to upload...",
    ]


def data_preview_default_message():
    return html.Span("Upload data to see preview", className="help-msg")


def settings_preview_default_message():
    return html.Span("Upload settings file to see preview", className="help-msg")


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
                        max_size=5000000,  # 5MB
                    ),
                ],
                className="card-body",
            ),
            className=f"card drop-card {addional_class}",
        ),
        className="col-lg-6",
    )


def create_criteria_table(params_dict, disabled=False):
    criteria_table_header = html.Thead(
        html.Tr(
            [
                html.Th("Criterion", className="text-start"),
                html.Th("Id", className="text-center"),
                html.Th("Weight", className="text-end"),
                html.Th("Expert min", className="text-end"),
                html.Th("Expert max", className="text-end"),
                html.Th("Objective", className="text-center"),
            ]
        )
    )
    criteria_table_body = html.Tbody(
        [
            html.Tr(
                [
                    html.Td(
                        children=criterion,
                        id=(
                            {"type": "criterion", "index": criterion}
                            if not disabled
                            else ""
                        ),
                    ),
                    html.Td(
                        daq.BooleanSwitch(
                            id=(
                                {"type": "id_column", "index": criterion}
                                if not disabled
                                else ""
                            ),
                            color="#0d6efd",
                            on=params_dict[criterion]["id_column"] == "true",
                        ),
                    ),
                    html.Td(
                        (
                            dcc.Input(
                                id={"type": "weight", "index": criterion},
                                value=params_dict[criterion]["weight"],
                                type="number",
                                min=0,
                                className="form-control text-end",
                            )
                            if not disabled
                            else html.Div(
                                params_dict[criterion]["weight"],
                                className="text-end",
                                style=(
                                    NO_STYLE
                                    if params_dict[criterion]["id_column"] == "false"
                                    else INVISIBLE
                                ),
                            )
                        ),
                    ),
                    html.Td(
                        (
                            dcc.Input(
                                id={"type": "expert_min", "index": criterion},
                                value=params_dict[criterion]["expert_min"],
                                type="number",
                                className="form-control text-end",
                            )
                            if not disabled
                            else html.Div(
                                params_dict[criterion]["expert_min"],
                                className="text-end",
                                style=(
                                    NO_STYLE
                                    if params_dict[criterion]["id_column"] == "false"
                                    else INVISIBLE
                                ),
                            )
                        ),
                    ),
                    html.Td(
                        dcc.Input(
                            id={"type": "expert_max", "index": criterion},
                            value=params_dict[criterion]["expert_max"],
                            type="number",
                            className="form-control text-end",
                        )
                        if not disabled
                        else html.Div(
                            params_dict[criterion]["expert_max"],
                            className="text-end",
                            style=(
                                NO_STYLE
                                if params_dict[criterion]["id_column"] == "false"
                                else INVISIBLE
                            ),
                        )
                    ),
                    html.Td(
                        daq.ToggleSwitch(
                            id=(
                                {"type": "objective", "index": criterion}
                                if not disabled
                                else ""
                            ),
                            label=["min", "max"],
                            color="#1ec283",
                            value=params_dict[criterion]["objective"] == "max",
                            style=(
                                NO_STYLE
                                if params_dict[criterion]["id_column"] == "false"
                                else INVISIBLE
                            ),
                        )
                    ),
                ]
            )
            for criterion in params_dict.keys()
        ]
    )

    criteria_table = html.Table(
        [criteria_table_header, criteria_table_body],
        className="table table-striped table-responsive criteria-table",
        style=NO_STYLE if not disabled else {"pointer-events": "none"},
    )

    return html.Div(criteria_table, className="col-lg-12 block-row")


def create_spinner(message):
    return (
        html.B(
            [
                message,
                " ",
                dbc.Spinner(color="#F77A18", size="sm"),
            ]
        ),
    )
