import dash
from dash import html

dash.register_page(__name__)

layout = html.Div(
    className="error-page-content text-center",
    children=[
        html.Img(
            className="error-img", src=dash.get_asset_url("img/pad_404.svg"), alt="404"
        ),
        html.Div(
            className="error-info",
            children="The page you're looking for was not found.",
        ),
        html.Div(
            className="error-action",
            children=html.A(
                className="btn btn-outline-primary btn-lg",
                href="/",
                children="Go to main site",
            ),
        ),
    ],
)
