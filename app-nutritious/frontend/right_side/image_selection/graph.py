from dash import html, dcc
from functions.dash_components import generate_radio_items, generate_dropdown
from functions.dash_figures import blank_figure

# Default setup
default_graphic_option = "Distribution"

def generate_graphic_products(pos, translations_init, nutrients, initial_language):
    return html.Div(id=f'graphic_gestion_{pos}', style={'display': 'None'}, children=[
        
        html.Hr(style={'border-top': '4px solid black'}),  # Horizontale line
        # RadioItems of graphic option
        html.Div([
            generate_radio_items(['Distribution', 'Products'],  #'Radarplot', 
                default_graphic_option, f'check_list_graph_img_{pos}', translations = translations_init)
        ], style={'margin': 'auto'}),

        # Dropdown for the macronutrient choice
        html.Div([
            generate_dropdown(None, nutrients, translations_init['choose_nutrients'], True, f'dropdown_nutrients_img_{pos}')
        ], style={'margin': '0 auto'}),

        # Figure of macronutriments
        html.Div([
            dcc.Graph(figure = blank_figure(initial_language), id=f'graph_products_img_{pos}', style={'height': '600px', 'width': '100%', 'float': 'center'}),
        ], style={'display': 'flex', 'flex-direction': 'row', 'width': '100%'}),
    ])