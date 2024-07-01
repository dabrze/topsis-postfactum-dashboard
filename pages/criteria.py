import pandas as pd
import dash
from dash import html, dcc, no_update, callback
from dash.dependencies import Input, Output, State

from common.layout_elements import stepper_layout


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
                "Set criteria ranges and weights:", className="col-lg-12 block-row"
            ),
            className="row",
        ),
        html.Div(
            "TODO",
            className="row block-row",
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
                        id="upload-submit-btn",
                        className="btn btn-primary",
                        disabled=True,
                    ),
                    href="/model",
                ),
            ],
            className="stepper-form-controls",
        ),
    ],
)


def get_callbacks(app):
    pass
