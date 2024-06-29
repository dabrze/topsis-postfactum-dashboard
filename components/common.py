import dash_bootstrap_components as dbc
from dash_dangerously_set_inner_html import DangerouslySetInnerHTML
from dash import html


EXTERNAL_STYLESHEETS = [
    dbc.themes.BOOTSTRAP,
    "https://cdn.jsdelivr.net/npm/bs-stepper/dist/css/bs-stepper.min.css",
    "https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap",
    "https://fonts.googleapis.com/css2?family=Roboto+Mono&display=swap",
    "https://fonts.googleapis.com/css2?family=Raleway:wght@400&display=swap",
    dbc.icons.FONT_AWESOME,
]


EXTERNAL_SCRIPTS = [
    dict(
        {
            "src": "https://code.jquery.com/jquery-3.4.1.min.js",
            "integrity": "sha256-CSXorXvZcTkaix6Yvo6HppcZGetbYMGWSFlBw8HfCJo=",
            "crossorigin": "anonymous",
        }
    ),
    {
        "src": "https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js",
        "integrity": "sha384-Q6E9RHvbIyZFJoft+2mJbHaEWldlvI9IOYy5n3zV9zzTtmI3UksdQRVvoxMfooAo",
        "crossorigin": "anonymous",
    },
    {
        "src": "https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js",
        "integrity": "sha384-wfSDF2E50Y2D1uUdj0O3uMBJnjuUD4Ih7YwaYd1iqfktj0Uod8GCExl3Og8ifwB6",
        "crossorigin": "anonymous",
    },
]


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
    app, step1_state="", step2_state="", step3_state="", step4_state="", content=""
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
                                html.Div(
                                    [
                                        html.Span("1", className="bs-stepper-circle"),
                                        html.Span(
                                            "Welcome", className="bs-stepper-label"
                                        ),
                                    ],
                                    className="step-trigger",
                                ),
                                className=f"step {step1_state}",
                            ),
                            html.Div(className="line"),
                            html.Div(
                                html.Div(
                                    [
                                        html.Span("2", className="bs-stepper-circle"),
                                        html.Span(
                                            "Upload data", className="bs-stepper-label"
                                        ),
                                    ],
                                    className="step-trigger",
                                ),
                                className=f"step {step2_state}",
                            ),
                            html.Div(className="line"),
                            html.Div(
                                html.Div(
                                    [
                                        html.Span("3", className="bs-stepper-circle"),
                                        html.Span(
                                            "Set criteria", className="bs-stepper-label"
                                        ),
                                    ],
                                    className="step-trigger",
                                ),
                                className=f"step {step3_state}",
                            ),
                            html.Div(className="line"),
                            html.Div(
                                html.Div(
                                    [
                                        html.Span("4", className="bs-stepper-circle"),
                                        html.Span(
                                            "Select model", className="bs-stepper-label"
                                        ),
                                    ],
                                    className="step-trigger",
                                ),
                                className=f"step {step4_state}",
                            ),
                        ],
                        className="bs-stepper-header",
                    ),
                    html.Div(content, className="bs-stepper-content"),
                ],
                id="submit-stepper",
                className="bs-stepper vertical col-lg-8 col-md-12",
            ),
            html.Div(
                html.Img(
                    id="pad-background",
                    className="img-fluid",
                    src=app.get_asset_url("img/pad_schematic.png"),
                    alt="Postfactum splash",
                ),
                className="col-lg-4 d-none d-lg-block",
            ),
        ],
        className="row",
    )