from dash_dangerously_set_inner_html import DangerouslySetInnerHTML
from dash import html
from dash import dcc

from components.common import stepper_layout


def upload_view():
    pass


def preview_view():
    pass


def upload_card(title, upload_id, store_id, multiple=False, optional=False):
    """
    Create a card component with an upload feature.

    Parameters:
    title (str): The title of the card.
    upload_id (str): The ID of the upload component.
    store_id (str): The ID of the store component.
    multiple (bool, optional): Whether multiple files can be uploaded. Defaults to False.
    optional (bool, optional): Whether the upload is optional. Defaults to False.

    Returns:
    dash_html_components.Div: The card component with the upload feature.
    """
    addional_class = "optional" if optional else ""

    return html.Div(
        html.Div(
            html.Div(
                [
                    html.H5(title, className="card-title"),
                    dcc.Upload(
                        html.Div(
                            [
                                html.I(className="fa-solid fa-cloud-arrow-up"),
                                " Drop file here or",
                                html.Br(),
                                "click to upload...",
                            ],
                            className="dz-default dz-message",
                        ),
                        multiple=multiple,
                        className="dropzone dz-clickable",
                        id=upload_id,
                    ),
                    dcc.Store(
                        id=store_id,
                        data=None,
                    ),
                ],
                className="card-body",
            ),
            className=f"card drop-card {addional_class}",
        ),
        className="col-lg-6",
    )


def upload_layout(app):
    """
    Generates the layout for the home page of the TOPSIS Postfactum Dashboard.

    Args:
        app (dash.Dash): The Dash application object.

    Returns:
        dash.html.Div: The generated HTML layout for the home page.
    """
    return stepper_layout(
        app,
        step2_state="active",
        content=[
            html.Div(
                html.Div("Upload files", className="col-lg-12 block-row"),
                className="row",
            ),
            html.Div(
                [
                    upload_card(
                        "CSV file",
                        "wizard-data-input-upload-data",
                        "wizard_state_stored-data",
                    ),
                    upload_card(
                        "JSON params file (optional)",
                        "wizard-data-input-upload-params",
                        "wizard_state_stored-params",
                        optional=True,
                    ),
                ],
                className="row block-row",
            ),
            html.Div(
                [
                    html.Div(id="wizard-data-output-parsed-data-before"),
                    html.Div(id="wizard-data-output-parsed-params"),
                    html.Div(id="data-preview"),
                ],
                id="data-preview-content",
            ),
            html.Div(id="data-table", style={"display": "none"}),
            html.Div(
                html.Button(
                    "Submit",
                    id="wizard_data_input_submit-button",
                    className="submit-button",
                    style={"display": "none"},
                ),
                id="nav-buttons",
            ),
        ],
    )
