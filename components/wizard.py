from dash_dangerously_set_inner_html import DangerouslySetInnerHTML
from dash import html

from components.common import stepper_layout


def wizard_layout(app):
    return html.Div(
        [
            html.Div(
                DangerouslySetInnerHTML(
                    stepper_layout(
                        step2_state="active",
                        content="""TODO
                                                       """,
                    )
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
