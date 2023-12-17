from dash import html, dcc, get_asset_url

# Importing the functions
from functions.dash_components import generate_slider, generate_dropdown, generate_radio_items, generate_input, generate_button
from functions.data_handling import pnns_groups_options
from frontend.style import return_style10, return_style15, return_style16

# Default setup
default_country = "France"
default_search_option = "product_name"

def generating_navigating_panel(option_languages, translations_init, initial_language, unique_countries, pnns_groups_1, pnns_groups_2, pnns_groups, products_availability, versionning):
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
                    generate_dropdown(translations_init[default_country], unique_countries, translations_init['choose_country'], False, 'dropdown_country', False)
                ], style={'margin': '0 auto'}),

                # Searchbar products // Dropdown
                html.Div([
                    generate_dropdown(None, [], translations_init['search_product'], False, 'search_bar')
                ], style={'margin': '0 auto', 'direction': 'ltr'}),
                
                # RadioItems of graphic option
                html.Div([
                    generate_radio_items(['product_name', 'product_code'], 
                                         default_search_option, 'type_search_product', translations = translations_init)
                ], style={'margin': '0 auto', 'direction': 'ltr'}),

                # pnns_groups_search with an image // Button
                html.Div([
                    html.A( 
                        generate_button(translations_init['picture_search_beta'], "picture_search_button", return_style15()),
                        href='#search_by_image')
                ], style={'margin': '0 auto'}),
            
                # Advanced searchbar products // Button
                html.Div([
                    generate_button(translations_init['advanced_search'], "advanced_search_button", return_style15())
                ], style={'margin': '0 auto'}),
            
                # History button
                html.Div([
                    generate_button(translations_init['browsing_history'], "browsing_button", return_style15())
                ], style={'margin': '0 auto', 'margin-bottom': '20px'}),

                html.Div([
                    dcc.Loading(id="loading_section_pnns", type="default", children = [
                        html.Div([
                            generate_button(pnns1["label"], pnns1["value"], return_style16()),
                            generate_button(pnns2["label"], pnns2["value"], return_style10())
                        ], style={'display': 'flex', 'flex-direction': 'column', 'width': '100%'}) 

                        if y == 0 and str(pnns1["value"]) != str(pnns2["value"]) else 

                            generate_button(pnns1["label"], pnns1["value"], return_style16())

                        if str(pnns1["value"]) == str(pnns2["value"]) else

                            generate_button(pnns2["label"], pnns2["value"], return_style10())

                        for pnns1 in pnns_groups_options(default_country, "pnns_groups_1", initial_language)
                        for y, pnns2 in enumerate(pnns_groups_options(default_country, "pnns_groups_2", initial_language, pnns1["value"]))
                    ]),
                ]),

                 dcc.Dropdown(
                    id='dropdown_number_product',
                    options=[
                        {'label': translations_init[f'displaying_{n}_products'], 'value': n}
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

                    html.Div(id='referencing', className='row', children=f"{translations_init['referenced_products']}: {products_availability}"),
                ], style={'textAlign': 'left', 'color': 'black', 'fontSize': 12}),
            ], style={'direction': 'ltr'}),
            ], style={'background-color': '#F0F0F0', 'overflowY': 'scroll', 'height': '100vh', 'flex': '1', 'direction': 'rtl',
                     'border-right': '1px solid black', 'margin':'0px'})