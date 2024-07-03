import dash
from dash import html

from common.layout_elements import stepper_layout


dash.register_page(
    __name__,
    title="Postfactum Analysis Dashboard: Select model",
    description="TOPSIS visualization and postfactum analysis dashboard.",
    image="img/pad_logo.png",
)

layout = stepper_layout(
    step4_state="active",
    show_background=True,
    content=[
        html.Div(
            html.Div(
                "Select TOPSIS model:",
                className="col-lg-12 section-header first-header",
            ),
            className="row",
        ),
        html.Div(
            "TODO",
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
                    href="/criteria",
                ),
                html.A(
                    html.Button(
                        "Next",
                        id="model-submit-btn",
                        className="btn btn-primary",
                        disabled=True,
                    ),
                    href="/dashboard",
                ),
            ],
            className="stepper-form-controls",
        ),
    ],
)
