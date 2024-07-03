import dash
from dash_dangerously_set_inner_html import DangerouslySetInnerHTML

dash.register_page(
    __name__,
    title="Postfactum Analysis Dashboard: About",
    description="TOPSIS visualization and postfactum analysis dashboard.",
    image="img/pad_logo.png",
)

layout = DangerouslySetInnerHTML(
    """
    <h2>About</h2>
    <p>Postfactum Analysis Dashboard is a tool for post-factum analysis for the TOPSIS
    multi-criteria ranking method. The dashboard lets users visualize TOPSIS rankings
    in WMSD-space and search for ways of improving the ranking positions of alternatives.
    The server offers methods for post-factum analysis that work on single criteria or
    the means/standard deviations of the alternative's criteria values.</p>
    <h3>How to use the server?</h3>
    <p>Go to the main page, upload your data, set criteria weights and ranges, analyze
    the TOPSIS ranking, and generate postfactum suggestions. For a step by step tutorial
    take the <a href="javascript:tour();">Tour</a>.</p>
    <h3>How does it work?</h3>
    <p>Documentation in progress...</p>
    <h3>Credits and attributions</h3>
    <p><b><a href="https://plotly.com/dash/">Plotly Dash</a></b> is licensed under the <a href="http://opensource.org/licenses/MIT">MIT license</a>.</p>
    <p><b><a href="http://getbootstrap.com">Bootstrap</a></b> by Twitter is licensed under the <a href="http://opensource.org/licenses/MIT">MIT license</a>.</p>
    <p><b><a href="http://jquery.org">jQuery</a></b> is licensed under the <a href="http://opensource.org/licenses/MIT">MIT license</a>.</p>
    <p><b><a href="http://fortawesome.github.io/Font-Awesome/">Font Awesome</a></b> is created by Dave Gandy and licensed under the <a href="http://scripts.sil.org/OFL">SIL Open Font License</a>.</p>
    <p><b><a href="https://fonts.google.com/specimen/Roboto">Roboto</a></b>, <b><a href="https://fonts.google.com/specimen/Roboto+Mono">Roboto Mono</a></b>, and <b><a href="https://fonts.google.com/specimen/Raleway">Raleway</a></b> are licensed under the <a href="http://scripts.sil.org/OFL">SIL Open Font License</a>.</p>

    <h3>Funding</h3>
    <p>The work was supported by the National Science Centre, Poland, grant number: 2022/47/D/ST6/01770.</p>
"""
)
