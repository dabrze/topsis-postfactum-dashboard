from dash_dangerously_set_inner_html import DangerouslySetInnerHTML
from dash import html

from components.common import stepper_layout


def home_page_layout(app):
    """
    Generates the layout for the home page of the TOPSIS Postfactum Dashboard.

    Args:
        app (dash.Dash): The Dash application object.

    Returns:
        dash.html.Div: The generated HTML layout for the home page.
    """
    return stepper_layout(
        app,
        step1_state="active",
        content="""
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
                          """,
    )
