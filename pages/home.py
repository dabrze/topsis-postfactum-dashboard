import dash

from dash_dangerously_set_inner_html import DangerouslySetInnerHTML
from dash import html

from common.layout_elements import stepper_layout

dash.register_page(
    __name__,
    path="/",
    title="Postfactum Analysis Dashboard",
    description="TOPSIS visualization and postfactum analysis dashboard.",
    image="img/pad_logo.png",
)


layout = stepper_layout(
    step1_state="active",
    content=DangerouslySetInnerHTML(
        """
    <div class="panel task-select-table">
        <div class="row">
                <div class="col-md-6 task-panel"">
                <a href="/upload" style="display: block">
                    <i class="fa-solid fa-upload task-select-img"></i>
                    <h3 class="task-select-header">Upload data</h3>
                    <p class="stepper-description-box">We will analyze <b>your data</b> by uploading it to the server,
                    setting the criteria weights, and running TOPSIS. Then you will be able to perform
                    postfactum analyses and discover how to change alternatives to reach given goals.</p>
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
                          """
    ),
)
