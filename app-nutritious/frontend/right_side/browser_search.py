from dash import html
from functions.dash_components import generate_table

# Browser history page

# We return a Html.Div that contains everything for the Browser history page
def generating_browser_history_page():
    return html.Div([
        html.Div(
            generate_table(None, 20, 'browser_table'),  
        )
    ], style={'display': 'None'},  id='browser_history_div')