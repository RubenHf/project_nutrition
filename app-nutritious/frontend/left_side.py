from dash import html, dcc, get_asset_url

# Importing the functions
from functions.dash_components import generate_slider, generate_dropdown, generate_radio_items, generate_input, generate_button
from functions.data_handling import pnns_groups_options

versionning = "0.7.1"

# Set default language
initial_language = 'en'

nutrients = ["fat_100g", "saturated-fat_100g", "carbohydrates_100g", "fiber_100g", "proteins_100g", "salt_100g", "macronutrients_100g"]

slider_trigger = ["slider_energy", "slider_fat", "slider_saturated", "slider_carbohydrates", "slider_fiber", "slider_proteins", "slider_salt", "slider_macronutrients"]

diets = ["Healthier foods", "Fiber rich foods", "Low sugar foods", "Protein rich foods", "Low fat foods", "Low salt foods", "Low saturated fat foods", "Energy rich foods"]

# Default setup
default_country, default_pnns1, default_diet = "France", "Fruits and vegetables", "Healthier foods" 
default_graphic_option, default_search_option = "Distribution", "product_name"

# to handle increased number of diet
TOTAL_IMAGES = len(diets) * 20

# To have a clearer code

style24 = {'font-size': '24px', 'color': 'black', 'width': '100%', 
            'textAlign': 'center', 'margin': '0px', 'border': 'none', 'background-color': 'gray',
            'display': 'flex', 'flex-direction': 'column'}

style16 = {'font-size': '16px', 'color': 'black', 'width': '100%', 
        'textAlign': 'left', 'margin': '0px', 'border': 'none', 'background-color': 'gray'}

style16_nd = {'font-size': '16px', 'color': 'black', 'width': '100%', 
        'textAlign': 'center', 'margin': '0px', 'border': '1px solid black', 'background-color': 'lightgray'}

style15 = {'align-items': 'center', 'justify-content': 'center', 'border': '1px solid black',
        'font-size': '15px', 'color': 'black', 'width': '100%', 
        'textAlign': 'center', 'margin': '0px', 'background-color': 'white'}

style10 = {'font-size': '10px', 'color': 'black', 'width': '100%', 'display':'none', 
        'textAlign': 'left', 'margin': '0px', 'border': 'none', 'background-color': 'gray'}



def generating_front_side(option_languages, translations, unique_countries, pnns_groups_1, pnns_groups_2, pnns_groups, products_availability):
    return html.Div(id='left_panel', children=[    
            html.Div(id='left_panel_div1', children=[  
                # For closing or opening the left panel
                html.Button('←', id='arrow_button_panel', 
                    style={'font-size': '48px', 'padding': '0', 'margin': '0', 'border': 'none'})
            ]),
    
            html.Div(id='left_panel_div2', children=[     
                html.Div(
                    html.Img(src=get_asset_url('pomme.jpeg'), 
                         style={'width': '300px', 'height': '300px'}),
                    style={'textAlign': 'center'}),

                # Title of the app/dashboard
                html.Div(className='row', children="Nutritious app",
                         style={'textAlign': 'center', 'color': 'black', 'fontSize': 48}),
            
                # Language dropdown
                html.Div([
                    generate_dropdown(initial_language, option_languages, None, False, 'dropdown_language', False)
                ], style={'margin': '0 auto'}),

                # Horizontale line
                html.Hr(style={'border-top': '4px solid black'}),  

                # Dropdown for the countries // Dropdown
                html.Div([
                    generate_dropdown(translations[initial_language][default_country], unique_countries, translations[initial_language]['choose_country'], False, 'dropdown_country', False)
                ], style={'margin': '0 auto'}),

                # Searchbar products // Dropdown
                html.Div([
                    generate_dropdown(None, [], translations[initial_language]['search_product'], False, 'search_bar')
                ], style={'margin': '0 auto', 'direction': 'ltr'}),
                                # RadioItems of graphic option
                html.Div([
                    generate_radio_items(['product_name', 'product_code'], 
                                         default_search_option, 'type_search_product', translations = translations[initial_language])
                ], style={'margin': '0 auto', 'direction': 'ltr'}),

                # pnns_groups_search with an image // Button
                html.Div([
                    generate_button(translations[initial_language]['picture_search_beta'], "picture_search_button", style15)
                ], style={'margin': '0 auto'}),
            
                # Advanced searchbar products // Button
                html.Div([
                    generate_button(translations[initial_language]['advanced_search'], "advanced_search_button", style15)
                ], style={'margin': '0 auto'}),
            
                # History button
                html.Div([
                    generate_button(translations[initial_language]['browsing_history'], "browsing_button", style15)
                ], style={'margin': '0 auto', 'margin-bottom': '20px'}),

                html.Div([
                    dcc.Loading(id="loading_section_pnns", type="default", children = [
                        html.Div([
                            generate_button(pnns1["label"], pnns1["value"], style16),
                            generate_button(pnns2["label"], pnns2["value"], style10)
                        ], style={'display': 'flex', 'flex-direction': 'column', 'width': '100%'}) 

                        if y == 0 and str(pnns1["value"]) != str(pnns2["value"]) else 

                            generate_button(pnns1["label"], pnns1["value"], style16)

                        if str(pnns1["value"]) == str(pnns2["value"]) else

                            generate_button(pnns2["label"], pnns2["value"], style10)

                        for pnns1 in pnns_groups_options(default_country, "pnns_groups_1", initial_language)
                        for y, pnns2 in enumerate(pnns_groups_options(default_country, "pnns_groups_2", initial_language, pnns1["value"]))
                    ]),
                ]),

                 dcc.Dropdown(
                    id='dropdown_number_product',
                    options=[
                        {'label': translations[initial_language][f'displaying_{n}_products'], 'value': n}
                        for n in [5, 10, 15, 20]
                    ],
                    clearable=False,
                    value=10,  # Set the default value
                    style={'font-size': '20px', 'color': 'black', 
                           'cursor': 'pointer', 'textAlign': 'center'}
                ),

                # Informations
                html.Div([
                    html.Div(className='row', children="Ruben HALIFA"),

                    html.Div(className='row', children=f"Version: {versionning}"),

                    html.Div(id='referencing', className='row', children=f"{translations[initial_language]['referenced_products']}: {products_availability}"),
                ], style={'textAlign': 'left', 'color': 'black', 'fontSize': 12}),
            ]),
            ], style={'background-color': '#F0F0F0', 'overflowY': 'scroll', 'height': '100vh', 'flex': '1', 'direction': 'rtl',
                     'border-right': '1px solid black', 'margin':'0px'})