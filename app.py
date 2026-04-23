import dash
import diskcache
from dash import html, dcc, DiskcacheManager
import dash_bootstrap_components as dbc

from common.layout_elements import (
    EXTERNAL_SCRIPTS,
    EXTERNAL_STYLESHEETS,
    footer,
    header,
)
from common.server_setup import parse_server_args

_cache = diskcache.Cache("./.dash-cache")
background_callback_manager = DiskcacheManager(_cache)

app = dash.Dash(
    __name__,
    external_stylesheets=EXTERNAL_STYLESHEETS,
    external_scripts=EXTERNAL_SCRIPTS,
    use_pages=True,
    suppress_callback_exceptions=True,
    background_callback_manager=background_callback_manager,
)

app.layout = dbc.Container(
    [
        header(app),
        html.Div(dash.page_container, className="container", id="page-content"),
        dcc.Store(id="data-store", storage_type="session"),
        dcc.Store(id="data-filename-store", storage_type="session"),
        dcc.Store(id="params-store", storage_type="session"),
        dcc.Store(id="params-filename-store", storage_type="session"),
        dcc.Store(id="colorscale-store", storage_type="local"),
        dcc.Store(id="precision-store", storage_type="local"),
        footer(),
    ],
    id="pad-layout",
    fluid=True,
)

app.title = "Postfactum Analysis Dashboard"
app._favicon = "img/pad_logo.png"


if __name__ == "__main__":
    args = parse_server_args()

    if args.port == 443:
        app.run(debug=args.debug, host=args.ip, port=args.port, ssl_context="adhoc")
    else:
        app.run(debug=args.debug, host=args.ip, port=args.port)
