import dash_bootstrap_components as dbc

from dash import dcc
from dash_dangerously_set_inner_html import DangerouslySetInnerHTML
from dash import html


external_stylesheets = [
    dbc.themes.BOOTSTRAP,
    "https://cdn.jsdelivr.net/npm/bs-stepper/dist/css/bs-stepper.min.css",
    "https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap",
    "https://fonts.googleapis.com/css2?family=Roboto+Mono&display=swap",
    "https://fonts.googleapis.com/css2?family=Raleway:wght@400&display=swap",
    dbc.icons.FONT_AWESOME,
]


external_scripts = [
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


def home_layout(app):
    return html.Div(
        [
            html.Div(
                DangerouslySetInnerHTML(
                    f"""
<div id="submit-stepper" class="bs-stepper vertical">
    <div class="bs-stepper-header">
        <div class="step active">
        <div class="step-trigger">
            <span class="bs-stepper-circle">1</span>
            <span class="bs-stepper-label">Welcome</span>
        </div>
        </div>
        <div class="line"></div>
        <div class="step">
        <div class="step-trigger">
            <span class="bs-stepper-circle">2</span>
            <span class="bs-stepper-label">Upload data</span>
        </div>
        </div>
        <div class="line"></div>
        <div class="step" >
        <div class="step-trigger">
            <span class="bs-stepper-circle">3</span>
            <span class="bs-stepper-label">Set criteria</span>
        </div>
        </div>
        <div class="line"></div>
        <div class="step">
        <div class="step-trigger">
            <span class="bs-stepper-circle">3</span>
            <span class="bs-stepper-label">Analyze</span>
        </div>
        </div>
    </div>
    <div class="bs-stepper-content">
        <div class="panel task-select-table">
            <div class="row">
                    <div class="col-md-6 task-panel"">
                    <a href="/wizard" style="display: block">
                        <i class="fa-solid fa-upload task-select-img"></i>
                        <h3 class="task-select-header">Upload data</h3>
                        <p class="stepper-description-box">We will analyze <b>your data</b> by uploading it to the server,
                        setting the criteria weights, and running TOPSIS. Then you will be able to perform
                        postfactum analyses and discover how to change an alternative to reach a given 
                        ranking position.</p>
                        <button type="button" class="btn btn-lg btn-outline-primary task-select-button">Upload</button>
                    </a>
                    </div>
                <div class="col-md-6 task-panel"">
                    <a href="/playground" style="display: block">
                        <i class="fa-regular fa-circle-play task-select-img"></i>
                        <h3 class="task-select-header">Use example</h3>
                        <p class="stepper-description-box">If you don't have a dataset at hand, you can test out the server 
                        using an <b>example dataset</b>. You will perform visualizations and postfactum analyses 
                        without having to submit your own data.<br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</p>
                        <button type="button" class="btn btn-lg btn-outline-primary task-select-button">Playground</button>
                    <a/>
                </div>
            </div>
        </div>
    </div>
</div>
"""
                ),
                className="col-lg-8 col-md-12",
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
