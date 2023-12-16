import dash
from dash import html, dcc, get_asset_url

# Importing the functions
from functions.dash_components import generate_slider, generate_dropdown, generate_radio_items, generate_input, generate_button, generate_table
from functions.dash_figures import blank_figure
from frontend.style import return_style16_nd, return_style24

# Default setup
default_graphic_option = "Distribution"

def generating_front_rightside(translations_init, initial_language, pnns_groups_1, pnns_groups_2, pnns_groups, diets, nutrients):

    return html.Div([
        # Advanced research
        html.Div([
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
                                            'width': '100%', 'background-color': '#F0F0F0', 'margin-bottom': '20px'}),

        
        html.Div([
            # Set an invisible anchor
            html.A(id="top_dash"),
            # To display a selected product at the top

            html.Div(id='selected_product_style', style={'display':'None'}, children=[
                dcc.Loading(id="loading_section_img", type="default", children = [
                    html.Div(id='selected_product_title',  
                        style=return_style24()),

                    # Searchbar for products with the same product name
                    html.Div([
                        generate_dropdown(None, [], translations_init['search_product'], False, 'multiple_product_dropdown')
                    ], style={'margin': '0 auto', 'border': '1px solid black'}),
                    
                    html.Div([
                        html.Img(id='selected_product_img', src=dash.get_asset_url('no_image.jpg'), 
                            alt=translations_init['no_image_available'], style = {'height':'450px', 'width':'450px'}),
                        html.Div(id='selected_product_texte')
                    ], style={'display': 'flex', 'flex-direction': 'row', 'width': '100%'}),

                    # To display up to 3 + 1 alternatives images
                    html.Div([
                        html.A( 
                            html.Img(id=f"selected_img_{i}", src=dash.get_asset_url('no_image.jpg'), n_clicks = 0, 
                                 alt=translations_init['no_image_available'], style={'height': '150px', 'width': '150px'}),
                            href='#top_dash')
                        for i in range(4)
                    ], style={'display': 'flex', 'flex-direction': 'row', 'width': '100%'}),
                ]),
            ]),

            # To display the list of products

            html.Div(id='images_title', 
                             style=return_style24()),

            html.Div([
                html.Div([
                    html.Button(children=f"{diet}", id=f"{diet}_div", n_clicks=0,
                                style={'font-size': '16px', 'color': 'black', 'textAlign': 'left', 'margin': '0px',
                                       'border': '1px', 'background-color': 'lightgray', 'width': '100%', 'margin': 'auto'}),
                    html.Div([
                        html.Div([
                            dcc.Loading(id=f"loading_section_{diet}_img_{i}", type="default", children = [
                            # html.A for having the clickable action on and going back to top
                            html.A( 
                                html.Img(id=f"{diet}_img_{i}", src=dash.get_asset_url('no_image.jpg'), n_clicks = 0, 
                                     alt=translations_init['no_image_available'], style={'height': '200px', 'width': '200px'}),
                            href='#top_dash'),
                            html.Div(id=f"{diet}_div_{i}")
                                ]),
                        ], style={'display': 'flex', 'flex-direction': 'column', 'width': '100%'})
                        for i in range(20)
                    ], style={'display': 'flex', 'flex-direction': 'row', 'overflowX': 'scroll'})
                    # Horizontal line
                ], style={'display': 'flex', 'flex-direction': 'column', 'width': '100%'})
                for diet in diets
            ]),

            html.Div(id='graphic_gestion', style={'display': 'None'}, children=[
                # Horizontale line
                html.Hr(style={'border-top': '4px solid black'}),  
                # RadioItems of graphic option
                html.Div([
                    generate_radio_items(['Distribution', 'Products'],  #'Radarplot', 
                                         default_graphic_option, 'check_list_graph_img', translations = translations_init)
                ], style={'margin': 'auto'}),

                # Dropdown for the macronutrient choice
                html.Div([
                    generate_dropdown(None, nutrients, translations_init['choose_nutrients'], True, 'dropdown_nutrients_img')
                ], style={'margin': '0 auto'}),

                # Figure of macronutriments
                html.Div([
                    dcc.Graph(figure = blank_figure(initial_language), id="graph_products_img", style={'height': '600px', 'width': '100%', 'float': 'center'}),
                ], style={'display': 'flex', 'flex-direction': 'row', 'width': '100%'}),
            ]),


        ], style={'display': 'block', 'flex-direction': 'row', 'width': '100%'},  id='images_gestion'),

        # To display the browser history
        html.Div([
            html.Div(
                generate_table(None, 20, 'browser_table'),  
            )
        ], style={'display': 'None'},  id='browser_history_div'),
        
        # To display the search by picture
        
        html.Div([
            # Maximum MB = 15
            dcc.Upload([
                    generate_button(html.Strong(translations_init['upload_image']), "upload_img_button", return_style16_nd()),
                ], max_size = 15 * 1024 * 1024, # Maximum file size to 15MB
                   accept=".jpeg, .png, .jpg",  # Accepted file types
                   style={'margin': '0 auto', 'float': 'center'}, id="upload_img_data"),
    
            # To show the uploaded image
            html.Div(id='uploaded_img', style={'margin': '0 auto', 'text-align': 'center'}),
            
            # To have the 2 buttons on the same row
            html.Div([
                
                html.Div([
                    generate_button(html.Strong(translations_init['search_pnns_groups_1']), "search_pnns1_img", {'display': 'None'}),
                ], style={'margin': '0 auto', 'text-align': 'left', 'width':'50%'}),
                
                html.Div([
                    generate_button(html.Strong(translations_init['search_pnns_groups_2']), "search_pnns2_img", {'display': 'None'}),
                ], style={'margin': '0 auto', 'text-align': 'right', 'width':'50%'}),
                
            ], style={'display': 'flex', 'flex-direction': 'row', 'width': '100%'}),
            
            html.Div([
                    generate_button(html.Strong(translations_init['clear_image']), "clear_img_button", {'display': 'None'}),
                ], style={'margin': '0 auto', 'float': 'center'}),
            
            # Div for the results
            html.Div([
                html.Div(style = {'margin-top': '10px'}),
            
                dcc.Graph(
                    id='model_figure_result',
                    config={'displayModeBar': False}
                ),

            ], style={'display':'None'}, id="result_model_image"),
            
            
        ], style={'display':'None'}, id='picture_search_div')
            
    ], style={'flex-direction': 'row', 'width': '100%', 'background-color': '#F0F0F0', 
              'overflowY': 'scroll', 'height': '100vh', 'flex': '2'})