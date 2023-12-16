from dash import html
from functions.dash_components import generate_slider, generate_dropdown, generate_input, generate_button
from frontend.style import return_style24

# Advanced search page

# We return a Html.Div that contains everything for the advanced search page
def generating_advanced_search_page(translations_init, pnns_groups_1, diets):
    return html.Div([
        html.Div([html.Strong(translations_init['advanced_search_label'])], 
                                style=return_style24()),
        
        # Dropdown for the pnns_groups_1
        html.Div([
            generate_dropdown(None, pnns_groups_1, translations_init['choose_pnns_group_1'], False, 'dropdown_pnns1')
        ], style={'width': '75%', 'margin': '0 auto', 'margin-bottom': '20px'}),

        # Dropdown for the pnns_groups_2
        html.Div([
            generate_dropdown(None, [], translations_init['choose_pnns_group_2'], False, 'dropdown_pnns2')
        ], style={'width': '75%', 'margin': '0 auto', 'margin-bottom': '20px'}),
        
        # Input to search product
        html.Div([
            generate_input(translations_init['search_product_optional'], "input_search_adv")
        ], style={'width': '75%', 'margin': '0 auto', 'margin-bottom': '20px'}),

        # Dropdown for the diet
        html.Div([
            generate_dropdown(None, diets, translations_init['choose_nutritious_plan'], False, 'dropdown_diet')
        ], style={'width': '75%', 'margin': '0 auto', 'margin-bottom': '20px'}),

        # Sliders controling which products we show
        html.Div([
            generate_slider(translations_init['energy_kcal_100g'], 'slider_energy', 3880),
            generate_slider(translations_init['fat_g_100g'], 'slider_fat', 100),
            generate_slider(translations_init['saturated_fat_g_100g'], 'slider_saturated', 100),
            generate_slider(translations_init['carbohydrates_g_100g'], 'slider_carbohydrates', 100),
            generate_slider(translations_init['fiber_g_100g'], 'slider_fiber', 100),
            generate_slider(translations_init['proteins_g_100g'], 'slider_proteins', 100),
            generate_slider(translations_init['salt_g_100g'], 'slider_salt', 100),
            generate_slider(translations_init['macronutrients_g_100g'], 'slider_macronutrients', 100)

            ], style={'float': 'center', 'width': '500px', 'margin':'0 auto', 'flex-direction': 'row', 'margin-bottom': '20px'}),

            # Button to reset options from the advanced search
        html.Div([
            generate_button(html.Strong("Reset"), "reset_sliders_button", {}),
        ], style={'float': 'center', 'margin':'0 auto', 'textAlign': 'center', 'color': 'black', 'fontSize': 15, 'margin-bottom': '20px'}),

        # Button to confirm the search 
        html.Div([
            generate_button(translations_init['search'], "search_confirmation_button", {'width': '200px'})
        ], style={'float': 'center', 'font-size': '12px', 'color': 'black', 'width': '200px', 'margin':'0 auto', 
                    'textAlign': 'center', 'border': '1px solid black', 'background-color': 'lightgray'}),

        # Horizontale line
        html.Hr(style={'border-top': '4px solid black'}),  
        
    ], id = 'advanced_search_div', style={'float': 'center', 'display': 'None', 'flex-direction': 'row', 
                                        'width': '100%', 'background-color': '#F0F0F0', 'margin-bottom': '20px'})