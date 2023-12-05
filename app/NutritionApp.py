import dash
from dash import Dash, html, dcc, Output, Input, State, ctx
import pandas as pd
import math
from io import StringIO
import time
from collections import Counter 

# Importing the functions
from app.dash_figures import create_figure_products
from app.dash_components import generate_slider, generate_dropdown, generate_button, generate_table, generate_radio_items
from app.data_handling import pnns_groups_options, return_df, get_image, get_code, mapping_nutriscore_IMG, df_sorting
from app.data_handling import get_data, products_by_countries,get_pnns_groups_1, get_pnns_groups_2, get_pnns_groups
from app.data_handling import generate_texte_image, get_texte_product, check_image_urls_parallel

# Linked to the external CSS file 

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', '/assets/styles.css']

app = Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)

server = app.server

app.title = 'Nutritious app'

versionning = "version: 0.6.6"

DEBUG = True

products_availability = "Referenced products: " + str(get_data().shape[0])

nutrients = ["fat_100g", "saturated-fat_100g", "carbohydrates_100g", "fiber_100g", "proteins_100g", "salt_100g", "macronutrients_100g"]

slider_trigger = ["slider_energy", "slider_fat", "slider_saturated", "slider_carbohydrates", "slider_fiber", "slider_proteins", "slider_salt", "slider_macronutrients"]

diets = ["Healthier foods", "Fiber rich foods", "Low sugar foods", "Protein rich foods", "Low fat foods", "Low salt foods", "Low saturated fat foods", "Energy rich foods"]

# Default setup
default_country, default_pnns1, default_diet = "France", "Fruits and vegetables", "Healthier foods" 
default_graphic_option, default_search_option = "Distribution", "Product name"

# Generate list of unique countries and number of products
unique_countries = products_by_countries()

# Generate pnns_groups 1 and 2, and sorted
pnns_groups_1 = get_pnns_groups_1()

pnns_groups_2 = get_pnns_groups_2()

pnns_groups = get_pnns_groups()
  
# to handle increased number of diet
TOTAL_IMAGES = len(diets) * 20

# To have a clearer code

style24 = {'font-size': '24px', 'color': 'black', 'width': '100%', 
            'textAlign': 'center', 'margin': '0px', 'border': 'none', 'background-color': 'gray',
            'display': 'flex', 'flex-direction': 'column'}

style16 = {'font-size': '16px', 'color': 'black', 'width': '100%', 
        'textAlign': 'left', 'margin': '0px', 'border': 'none', 'background-color': 'gray'}

style15 = {'align-items': 'center', 'justify-content': 'center', 'border': '1px solid black',
        'font-size': '15px', 'color': 'black', 'width': '100%', 
        'textAlign': 'center', 'margin': '0px', 'background-color': 'white'}

style10 = {'font-size': '10px', 'color': 'black', 'width': '100%', 'display':'none', 
        'textAlign': 'left', 'margin': '0px', 'border': 'none', 'background-color': 'gray'}

app.layout = html.Div([
    # Left side
    html.Div(id='left_panel', children=[    
        html.Div(id='left_panel_div1', children=[  
            # For closing or opening the left panel
            html.Button('←', id='arrow_button_panel', 
                style={'font-size': '48px', 'padding': '0', 'margin': '0', 'border': 'none'})
        ]),
    
        html.Div(id='left_panel_div2', children=[     
            html.Div(
                html.Img(src=dash.get_asset_url('pomme.jpeg'), 
                     style={'width': '300px', 'height': '300px'}),
                style={'textAlign': 'center'}),

            # Title
            html.Div(className='row', children="Nutritious app",
                     style={'textAlign': 'center', 'color': 'black', 'fontSize': 48}),

            # Horizontale line
            html.Hr(style={'border-top': '4px solid black'}),  

                # Dropdown for the countries // Dropdown
            html.Div([
                generate_dropdown(default_country, unique_countries, "Choose a country", False, 'dropdown_country', False)
            ], style={'margin': '0 auto', 'border': '1px solid black'}),

            # Searchbar products // Dropdown
            html.Div([
                generate_dropdown(None, [], "Search a product", False, 'search_bar')
            ], style={'margin': '0 auto', 'border': '1px solid black', 'direction': 'ltr'}),
                            # RadioItems of graphic option
            html.Div([
                generate_radio_items(['Product name', 'Product code'], 
                                     default_search_option, 'type_search_product')
            ], style={'margin': '0 auto', 'border': '1px solid black', 'direction': 'ltr'}),

            # Advanced searchbar products // Button
            html.Div([
                generate_button("Advanced search 🔍", "advanced_search_button", style15)
            ], style={'margin': '0 auto'}),
            
            # History button
            html.Div([
                generate_button("Browsing history", "browsing_button", style15)
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

                    for pnns1 in pnns_groups_options(default_country, "pnns_groups_1")
                    for y, pnns2 in enumerate(pnns_groups_options(default_country, "pnns_groups_2", pnns1["value"]))
                ]),
            ]),

             dcc.Dropdown(
                id='dropdown_number_product',
                options=[
                    {'label': 'Displaying 5 products', 'value': 5},
                    {'label': 'Displaying 10 products', 'value': 10},
                    {'label': 'Displaying 15 products', 'value': 15},
                    {'label': 'Displaying 20 products', 'value': 20},
                ],
                clearable=False,
                value=10,  # Set the default value
                style={'font-size': '20px', 'color': 'black', 'cursor': 'pointer',  
                       'textAlign': 'center', 'border': '1px solid black'}
            ),

            # Informations
            html.Div([
                html.Div(className='row', children="Ruben HALIFA"),

                html.Div(className='row', children=versionning),

                html.Div(className='row', children=products_availability),
            ], style={'textAlign': 'left', 'color': 'black', 'fontSize': 12}),
        ]),
        ], style={'background-color': '#F0F0F0', 'overflowY': 'scroll', 'height': '100vh', 'flex': '1', 'direction': 'rtl',
                 'border-right': '1px solid black', 'margin':'0px'}),

    # Contents on the right side
    html.Div([

            html.Div([
                html.Div([html.Strong("ADVANCED SEARCH")], 
                                     style=style24),
                
                # Dropdown for the pnns_groups_1
                html.Div([
                    generate_dropdown(None, pnns_groups_1, "Choose a PNNS group 1", False, 'dropdown_pnns1')
                ], style={'width': '75%', 'margin': '0 auto', 'margin-bottom': '20px'}),

                # Dropdown for the pnns_groups_2
                html.Div([
                    generate_dropdown(None, [], "Choose a PNNS group 2", False, 'dropdown_pnns2')
                ], style={'width': '75%', 'margin': '0 auto', 'margin-bottom': '20px'}),

                # Dropdown for the diet
                html.Div([
                    generate_dropdown("Healthier foods", diets, "Choose a nutritious plan", False, 'dropdown_diet', False)
                ], style={'width': '75%', 'margin': '0 auto', 'margin-bottom': '20px'}),

                # Sliders controling which products we show
                html.Div([
                    generate_slider("Energy kcal/100g", 'slider_energy', 3880),
                    generate_slider("Fat g/100g", 'slider_fat', 100),
                    generate_slider("Saturated_fat g/100g", 'slider_saturated', 100),
                    generate_slider("Carbohydrates g/100g", 'slider_carbohydrates', 100),
                    generate_slider("Fiber g/100g", 'slider_fiber', 100),
                    generate_slider("Proteins g/100g", 'slider_proteins', 100),
                    generate_slider("Salt g/100g", 'slider_salt', 100),
                    generate_slider("Macronutrients g/100g", 'slider_macronutrients', 100)

                    ], style={'float': 'center', 'width': '500px', 'margin':'0 auto', 'flex-direction': 'row', 'margin-bottom': '20px'}),

                    # Button to reset options from the advanced search
                html.Div([
                    generate_button(html.Strong("Reset"), "reset_sliders_button", {}),
                ], style={'float': 'center', 'margin':'0 auto', 'textAlign': 'center', 'color': 'black', 'fontSize': 15, 'margin-bottom': '20px'}),

                # Button to confirm the search 
                html.Div([
                    generate_button("Search", "search_confirmation_button", {'width': '200px'})
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
                        style=style24),

                    html.Div([
                        html.Img(id='selected_product_img', src=dash.get_asset_url('no_image.jpg'), 
                            alt="No image available", style = {'height':'450px', 'width':'450px'}),
                        html.Div(id='selected_product_texte')
                    ], style={'display': 'flex', 'flex-direction': 'row', 'width': '100%'}),

                    # To display up to 3 + 1 alternatives images
                    html.Div([
                        html.A( 
                            html.Img(id=f"selected_img_{i}", src=dash.get_asset_url('no_image.jpg'), n_clicks = 0, 
                                 alt="No image available", style={'height': '150px', 'width': '150px'}),
                            href='#top_dash')
                        for i in range(4)
                    ], style={'display': 'flex', 'flex-direction': 'row', 'width': '100%'}),
                ]),
            ]),

            # To display the list of products

            html.Div(id='images_title', 
                             style=style24),

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
                                     alt="No image available", style={'height': '200px', 'width': '200px'}),
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
                # RadioItems of graphic option
                html.Div([
                    generate_radio_items(['Radarplot', 'Distribution', 'Products'], 
                                         default_graphic_option, 'check_list_graph_img')
                ], style={'margin': 'auto'}),

                # Dropdown for the macronutrient choice
                html.Div([
                    generate_dropdown(None, nutrients, "Choose nutrients", True, 'dropdown_nutrients_img')
                ], style={'margin': '0 auto'}),

                # Figure of macronutriments
                html.Div([
                    dcc.Graph(id="graph_products_img", style={'height': '600px', 'width': '100%', 'float': 'center'}),
                ], style={'display': 'flex', 'flex-direction': 'row', 'width': '100%'}),
            ]),


        ], style={'display': 'block', 'flex-direction': 'row', 'width': '100%'},  id='images_gestion'),

    # To display the browser history
    html.Div([
        html.Div(
        generate_table(None, 20, 'browser_table'),  
        )
    ], style={'display': 'None'},  id='browser_history_div'),
            
    ], style={'flex-direction': 'row', 'width': '100%', 'background-color': '#F0F0F0', 
              'overflowY': 'scroll', 'height': '100vh', 'flex': '2'}),
    
    dcc.Store(id='sliced_file', data=None),
    dcc.Store(id='personnalized_sorting', data=None),
    dcc.Store(id='selected_product_table', data=None),
    dcc.Store(id='dropdown_search_bar_number', data=0),
    dcc.Store(id='dropdown_table_number', data=0),
    dcc.Store(id='initialization_graph', data = False),
    dcc.Store(id='pnns1_chosen', data=None),
    dcc.Store(id='pnns2_chosen', data=None),
    dcc.Store(id='search_on', data=False),
    dcc.Store(id='shown_img', data={f'{diet}_img_{i}': None for diet in diets for i in range(20)}),
    # To store the client navigation history
    dcc.Store(id='history', data=[]),
    dcc.Store(id='loading_history', data=False),
    
],id='app-container', style={'justify-content': 'space-between', 'margin': '0', 'padding': '0'})

@app.callback(
    Output('sliced_file', 'data'),
    
    *[Input(f'{slide}', 'value') for slide in slider_trigger],
    
    Input('dropdown_country','value'),
    Input('dropdown_pnns1','value'),
    Input('dropdown_pnns2','value'),
    
    Input('advanced_search_button', 'n_clicks'),
    
    prevent_initial_call=True,
)

def data_slicing(slide_energy, slide_fat, slide_sat_fat, slide_carbs, 
                 slide_fiber, slide_prot, slide_salt, slide_macro,
                 country, pnns1_chosen, pnns2_chosen, clicks):

    sliders = [slide_energy, slide_fat, slide_sat_fat, slide_carbs, slide_fiber, slide_prot, slide_salt, slide_macro]
    elapsed_time = time.time() if DEBUG else None
    
    # Returning no data to show
    if country is None:
        return None

    # It follow the same path for all
    df = return_df(country, pnns1_chosen, pnns2_chosen)

    for nutrient, slide in zip(["energy_100g"] + nutrients, sliders):
        df = df[(df[nutrient] >= slide[0]) & (df[nutrient] <= slide[1])]
    
    # Transform to json format
    df = df.to_json(orient='split')
    
    print("Data slicing", time.time() - elapsed_time) if DEBUG else None
    return df

    
@app.callback(
    Output('search_bar', 'options'),
    
    Input('dropdown_country','value'),
    Input('type_search_product','value'),
)

# We prepare the search_bar, changing when the country choice is different
def search_bar_option_def(country, dropdown_search):
    
    elapsed_time = time.time() if DEBUG else None
    
    # If we change pnns or country group, we change the bar_option
    df = return_df(country, None, None)
    
    # If we search by product name
    if dropdown_search == 'Product name':
        # Get a Series with unique product names and their counts using Counter
        unique_counts = Counter(df['product_name'])

        # Sort the unique product names
        sorted_names = sorted(unique_counts.keys())

        # Create the search_bar_option list
        search_bar_option = [
            {
                'label': f"{name} [{count} products]",
                'value': name
            }
            for name in sorted_names
            for count in [unique_counts[name]]
        ]
        
    # If we search by product code
    elif dropdown_search == 'Product code':
        # Each product has its own unique code
        
        # Create the search_bar_option list
        search_bar_option = [
            {
                'label': code,
                'value': code
            }
            for code in df['code'].unique()
        ]

    print("search_bar_option_def", time.time() - elapsed_time) if DEBUG else None
    return search_bar_option


@app.callback(
    *[Output(f'{pnns2}', 'style') for pnns2 in pnns_groups_2],
    *[Output(f'{pnns1}', 'children') for pnns1 in pnns_groups_1],
    *[Output(f'{pnns2}', 'children') for pnns2 in pnns_groups_2],
    Output("advanced_search_div", 'style', allow_duplicate=True),
    Output('images_gestion', 'style', allow_duplicate=True),
    Output('pnns1_chosen', 'data'),
    Output('pnns2_chosen', 'data'),
    Output('history', 'data', allow_duplicate=True),
    
    *[Input(f'{pnns1}', 'n_clicks') for pnns1 in pnns_groups_1],
    *[Input(f'{pnns2}', 'n_clicks') for pnns2 in pnns_groups_2],
    Input('dropdown_country','value'),
    Input('loading_history','data'),
    
    State('history', 'data'),
    State('pnns1_chosen', 'data'),
    State('pnns2_chosen', 'data'),
    
    prevent_initial_call=True,
)
def click_pnns_showing(*args):
    elapsed_time = time.time() if DEBUG else None
    
    pnns2_option_visible = {'font-size': '10px', 'color': 'black', 'width': '100%', 'display':'block', 
              'textAlign': 'left', 'margin': '0px', 'border': 'none', 'background-color':'#C5C5C5'}
    
    pnns2_option_invisible = {'display': 'none'}
    
    pnns2_clicked_on = {'font-size': '16px', 'color': 'black', 'width': '100%', 'display':'block', 
              'textAlign': 'left', 'margin': '0px', 'border': 'none', 'background-color':'#C5C5C5'}
    
    style_search_div = {'display': 'None'}
    
    # Display go to default for the right panel (set mainly for when we are in the browser history)
    style_images_gestion = {'display': 'block', 'flex-direction': 'row', 'width': '100%'}
    
    # We retrieve the last arguments
    country, history_nav, pnns2_chosen, pnns1_chosen = args[-5], args[-3], args[-1], args[-2] 
    
    # Initialize the display to none
    output_style = [pnns2_option_invisible] * len(pnns_groups_2) 
    output_label_pnns1 = [dash.no_update] * len(pnns_groups_1)
    output_label_pnns2 =  [dash.no_update] * len(pnns_groups_2)
    
    # Function changing the style of the pnns buttons
    def changing_style_pnns_button(output_style, pnns):
        i = 0
        for pnns1 in pnns_groups_1:
            for pnns2 in pnns_groups[pnns1]:
                if pnns1 == pnns2:
                    continue

                # if it is a pnns groups 1 that was clicked on
                elif pnns == pnns1:
                    output_style[i] = pnns2_option_visible

                # if it is a pnns groups 2 that was clicked on
                elif pnns in pnns_groups[pnns1]:
                    # we highlight the one clicked on
                    if pnns == pnns2:
                        output_style[i] = pnns2_clicked_on
                    else:
                        output_style[i] = pnns2_option_visible
                i += 1 # We increment
                
        return output_style
    
    # When a pnns_groups_1 or 2 was clicked on
    if ctx.triggered_id in pnns_groups_1 + pnns_groups_2:    
        output_style = changing_style_pnns_button(output_style, ctx.triggered_id)
    
    # When a pnns_groups_1 was clicked on
    if ctx.triggered_id in pnns_groups_1:
        
        pnns1_chosen = ctx.triggered_id
        pnns2_chosen = None
        
        # We add to the navigation history
        history_nav.insert(0, ["Navigation", country, ctx.triggered_id, pnns2_chosen, None, None])
    
    # When a pnns_groups_2 was clicked on
    elif ctx.triggered_id in pnns_groups_2:
        
        # We add to the navigation history
        history_nav.insert(0, ["Navigation", country, pnns1_chosen, ctx.triggered_id, None, None])
        
        pnns1_chosen = dash.no_update
        pnns2_chosen = ctx.triggered_id
                    
    # If loading from the browser history
    elif ctx.triggered_id == 'loading_history':
        # We retrieve the data
        pnns1_chosen, pnns2_chosen = args[-2], args[-1]
        
        # We check the pnns2 before pnns1
        pnns = pnns2_chosen if pnns2_chosen != None else pnns1_chosen
        
        # Modify the style of buttons
        output_style = changing_style_pnns_button(output_style, pnns)      
    
    # The country was change, we are modifying the title
    if ctx.triggered_id == 'dropdown_country':
        
        pnns1_chosen, pnns2_chosen = None, None
        
        # We add to the navigation history
        history_nav.insert(0, ["Navigation", country, pnns1_chosen, pnns2_chosen, None, None])
        
        # Product calcul
        pnns_groups_1_options = pnns_groups_options(country, "pnns_groups_1")
        
        # New label (= new number of products)
        output_label_pnns1 = [pnns1["label"] for pnns1 in pnns_groups_1_options]
        
        output_label_pnns2 = [
            pnns2["label"]
            for pnns1 in pnns_groups_1_options
            for pnns2 in pnns_groups_options(country, "pnns_groups_2", pnns1["value"])
            if str(pnns1["value"]) != str(pnns2["value"])
        ]
                        
    print("click_pnns_showing", time.time() - elapsed_time) if DEBUG else None
    
    output_values = [*output_style, *output_label_pnns1, *output_label_pnns2]
    output_values.extend([style_search_div, style_images_gestion, pnns1_chosen, pnns2_chosen, history_nav])

    return tuple(output_values)

@app.callback(
    *[
    Output(f"{slide}", property)
    for slide in slider_trigger
    for property in ['min', 'max', 'marks', 'value']
    ],
    Output("dropdown_pnns2", "options"), 
    Output("dropdown_pnns1", "value"), 
    Output("dropdown_pnns2", "value"), 
    Output("dropdown_diet", "value"), 
    
    Input("dropdown_pnns1", "value"), 
    Input("dropdown_pnns2", "value"), 
    Input('reset_sliders_button', 'n_clicks'),
    Input('advanced_search_button', 'n_clicks'),
    State('dropdown_country','value'),
    prevent_initial_call=True,
)
def update_sliders(pnns1_chosen, pnns2_chosen, n_clicks, n_clicks_search, country):
    elapsed_time = time.time() if DEBUG else None
            
    if ctx.triggered_id == "reset_sliders_button":
        pnns1_chosen, pnns2_chosen = None, None 
        pnns_groups_2 = []
        diet = default_diet
        # If the data change, we change the sliders
        df = return_df(country, pnns1_chosen, pnns2_chosen)
    
    else:
        if pnns2_chosen == 0:
            pnns2_chosen = 0
        df = return_df(country, pnns1_chosen, pnns2_chosen)
        if pnns1_chosen:
            pnns_groups_2 = pnns_groups[pnns1_chosen]
        else: 
            pnns_groups_2 = []
        diet = dash.no_update
    
    if isinstance(df, pd.DataFrame):
        output_values = []

        # Rounding down
        for nutrient in ["energy_100g"] + nutrients:
            nutrient_min = math.floor(df[f'{nutrient}'].min())
            nutrient_max = math.ceil(df[f'{nutrient}'].max())
            nutrient_marks = {nutrient_min: str(nutrient_min), nutrient_max: str(nutrient_max)}
            output_values.extend([nutrient_min, nutrient_max, nutrient_marks, [math.floor(nutrient_min), math.ceil(nutrient_max)]])

        print("update_sliders", time.time() - elapsed_time) if DEBUG else None
        output_values.extend([pnns_groups_2, pnns1_chosen, pnns2_chosen, diet])
        
        return tuple(output_values)

    return dash.no_update

"""@app.callback(
    *[Output(f'{diet}_img_{i}', 'style', allow_duplicate=True) for diet in diets for i in range(20)],
    
    *[Input(f'{diet}_div', 'n_clicks') for diet in diets],
    *[Input(f'{diet}_img_{i}', 'n_clicks') for diet in diets for i in range(20)],
    *[Input(f'{pnns1}', 'n_clicks') for pnns1 in pnns_groups_1],
    *[Input(f'{pnns2}', 'n_clicks') for pnns2 in pnns_groups_2],
    Input('dropdown_country','value'),
    Input('search_bar', 'value'),
    
    prevent_initial_call=True,
)
def clear_image(*args):
    
    output_values = [{'display':'None'}] * TOTAL_IMAGES
    
    return tuple(output_values)"""
    

@app.callback(
    Output('images_title', 'children'),
    *[Output(f'{diet}_div', 'children') for diet in diets],
    *[Output(f'{diet}_img_{i}', 'src') for diet in diets for i in range(20)],
    *[Output(f'{diet}_img_{i}', 'style') for diet in diets for i in range(20)],
    *[Output(f'{diet}_div_{i}', 'children') for diet in diets for i in range(20)],
    *[Output(f"selected_img_{i}", 'src') for i in range(4)],
    *[Output(f"selected_img_{i}", 'style') for i in range(4)],
    Output("graph_products_img", 'figure', allow_duplicate=True),
    Output("graphic_gestion", 'style'),
    Output('personnalized_sorting', 'data', allow_duplicate=True),
    Output("selected_product_style", 'style'),
    Output("selected_product_img", 'src'),
    Output("selected_product_title", 'children'),
    Output("selected_product_texte", 'children'),
    Output('advanced_search_div', 'style', allow_duplicate=True),
    Output('search_on', 'data'),
    Output('shown_img', 'data'),
    Output('history', 'data', allow_duplicate=True),
    
    *[Input(f'{diet}_div', 'n_clicks') for diet in diets],
    *[Input(f'{diet}_img_{i}', 'n_clicks') for diet in diets for i in range(20)],
    Input('pnns1_chosen', 'data'),
    Input('pnns2_chosen', 'data'),
    Input('dropdown_country','value'),
    Input('search_bar', 'value'),
    Input('search_confirmation_button', 'n_clicks'),
    Input('advanced_search_button', 'n_clicks'),
    
    State('type_search_product', 'value'),
    State('dropdown_nutrients_img', 'value'),
    State('check_list_graph_img','value'),
    State('personnalized_sorting', 'data'),
    State('sliced_file', 'data'),
    State("dropdown_diet", "value"), 
    State('search_on', 'data'),
    State('dropdown_number_product', 'value'),
    State('shown_img', 'data'),
    State('history', 'data'),
    
    prevent_initial_call=True,
)

def display_images(*args):
    elapsed_time = time.time() if DEBUG else None
    
    # We unpack the args
    (pnns1_chosen, pnns2_chosen, country, search_bar, clicked_search, click_advanced_search, type_search_product,
     nutrients_choice, ch_list_graph, selected_diet, df_slice, dropdown_diet, search_on, n_best,
     shown_img_data, history_nav) = args[-16:]
    
    # Return true if one of the diet was click.
    # It is helping for the browser history
    
    clicked_diet_ctx = [f'{diet}_div' for diet in diets]
    browser_diet = any(any(keyword in item['prop_id'] for keyword in clicked_diet_ctx) for item in ctx.triggered)
    
    # Initialize 
    no_display = {'display':'None'}
    images, styles_images, textes_images = [dash.no_update] * TOTAL_IMAGES, [no_display] * TOTAL_IMAGES, [None] * TOTAL_IMAGES
    others_img, others_img_style = [None] * 4, [no_display] * 4
    subtitles, title, figure = [None] * len(diets), None, dash.no_update 
    selected_product_img, selected_product_title, selected_product_texte = None, None, None
    graphic_gestion_style, selected_product_style, advanced_search_style = no_display, no_display, no_display
    search_on = False if search_on else dash.no_update
    selected_diet = None if selected_diet != None else dash.no_update
    
    # dataframe preparation, only when necessary
    if ctx.triggered_id not in ['advanced_search_button', 'search_confirmation_button']:
        
        df = return_df(country, pnns1_chosen, pnns2_chosen)
        
    elif ctx.triggered_id == 'search_confirmation_button':
        
        df = pd.read_json(StringIO(df_slice), orient='split')
        
    # If clicking on diet preference or confirmed search
    if (ctx.triggered_id in clicked_diet_ctx + ['search_confirmation_button']) or (browser_diet): 
        
        for i, diet in enumerate([diet + "_div" for diet in diets]):
            subtitles[i] = html.Strong(f"{diets[i]}")
            
            if (ctx.triggered_id in ['search_confirmation_button', diet]) or browser_diet: 
                
                # If client clicked on the confirmation button of the advanced search
                if ctx.triggered_id == 'search_confirmation_button':
                    if diet[:-4] == dropdown_diet:
                        selected_diet = diets[i] # To keep the selected button
                        advanced_search_style = dash.no_update
                        search_on = True
                
                # Elif client clicked on one of the diet button
                else:
                    # We check which one is in ctx.triggered
                    result = any(diet in item.get('prop_id', '') for item in ctx.triggered)
                    
                    # Add information when it is the selected diet
                    if (diet == ctx.triggered_id) or (result):
                        selected_diet = diets[i] # To keep the selected button
                        
                        # We add to the navigation history
                        history_nav.insert(0, ["Navigation", country, pnns1_chosen, pnns2_chosen, diets[i], None])
                
                if selected_diet == diets[i]:
                    
                    title = html.Strong(f"BEST RECOMMENDED PRODUCTS FOR {diets[i].upper()}")
                    
                    # sort and retrieve the N best, then match the nutriscore image           
                    df_N_best = mapping_nutriscore_IMG(df_sorting(diets[i], df).head(n_best))

                    for y, (_, row) in enumerate(df_N_best.iterrows()):
                        index = y if i == 0 else (20 * i) + y

                        styles_images[index] = {'height': '400px', 'width': '400px'}
                        
                        # generate the texte below the image
                        textes_images[index] = get_texte_product(row)

        # Creating a figure of the data distribution 
        figure = create_figure_products(df, nutrients, nutrients_choice, ch_list_graph, df_N_best)
        graphic_gestion_style = {'display':'block'}
        
    # When navigating on the left panel    
    elif ctx.triggered_id in ['pnns1_chosen', 'pnns2_chosen', 'dropdown_country']:
        
        title = html.Strong("BEST RECOMMENDED PRODUCTS BY CATEGORY")
        
        subtitles, images, styles_images, textes_images = generate_texte_image(df, diets, n_best, 
                                                                               subtitles, images, 
                                                                               styles_images, textes_images)
                                
    # If the client clicked on the search bar or one of the picture
    elif ctx.triggered_id in ["search_bar"] + [f'{diet}_img_{i}' for diet in diets for i in range(20)]:
        
        try:
            if ctx.triggered_id == "search_bar":
                # We check if it is a product name or code entered
                
                if type_search_product == "Product name":
                    df_product = get_data().query('product_name == @search_bar')
                elif type_search_product == "Product code":
                    df_product = get_data().query('code == @search_bar')

            else: 
                url = shown_img_data[ctx.triggered_id]
                code = get_code(url)
                df_product = get_data().query('code == @code')

            # We search for the product [Only one for now]
            df_product = df_product.head(1) if df_product.shape[0] > 1 else df_product

            df_product = mapping_nutriscore_IMG(df_product)
            
            # We get the product's name
            product_name = df_product['product_name'].values[0]
            
            # Principale image
            selected_product_img = get_image(str(df_product["code"].values[0]))
            
            # Secondaries images
            # Return the link of the image, then check it's validity
            others_img = check_image_urls_parallel([
                          get_image(str(df_product["code"].values[0]), i) 
                          for i in range(1, 5)])
            
            # Display image if link correct
            others_img_style = [{'height': '150px', 'width': '150px'}
                               if others_img[i] != None else no_display
                               for i in range(0, 4)]
            
            selected_product_title = html.Strong(product_name)
            selected_product_texte = get_texte_product(df_product.iloc[0])

            pnns1 = df_product["pnns_groups_1"].values[0]
            pnns2 = df_product["pnns_groups_2"].values[0]
                
            # We add to the navigation history
            history_nav.insert(0, [f"Product: {product_name}", country, pnns1, pnns2, None, code])
            
            df = return_df(country, pnns1, pnns2).copy()
        
            title = html.Strong("BEST RECOMMENDED PRODUCTS BY CATEGORY")

            subtitles, images, styles_images, textes_images = generate_texte_image(df, diets, n_best, 
                                                                                   subtitles, images, 
                                                                                   styles_images, textes_images)
            
            # Creating a figure of the data distribution 
            figure = create_figure_products(df, nutrients, nutrients_choice, ch_list_graph, df_product)
            graphic_gestion_style = {'display':'block'}
            
        except:
            selected_product_img = dash.get_asset_url("no_image.jpg")
            selected_product_title = html.Strong("Product not found, search for another one")
            selected_product_texte = html.Strong("The product is not available")

            title = dash.no_update
            subtitles = [dash.no_update] * len(diets)
            styles_images = [dash.no_update] * TOTAL_IMAGES
            textes_images = [dash.no_update] * TOTAL_IMAGES
            graphic_gestion_style = dash.no_update
        
        selected_product_style = {'display':'block'}
        
    elif ctx.triggered_id == 'advanced_search_button':
        
        advanced_search_style = {'float': 'center', 'display': 'block', 'flex-direction': 'row', 
                                'width': '100%', 'background-color': '#F0F0F0', 'margin-bottom': '20px'}
        
    # Top keep tract of the images src to load when clicking on 
    for i, src in enumerate(images):
        key = f'{diets[int(i/20)]}_img_{i%20}'
        if src == dash.no_update or src == None:
            continue
        else:
            shown_img_data[key] = src
            
    output_values = [title, *subtitles, *images, *styles_images, *textes_images, *others_img, *others_img_style,
                     figure, graphic_gestion_style, selected_diet, selected_product_style, 
                     selected_product_img, selected_product_title, selected_product_texte,
                     advanced_search_style, search_on, shown_img_data, history_nav]
    
    print("display_images: ", time.time() - elapsed_time) if DEBUG else None  
    return tuple(output_values)

@app.callback(
    Output("selected_product_img", 'src', allow_duplicate=True),
    
    *[Input(f"selected_img_{i}", 'n_clicks') for i in range(4)],
    
    *[State(f"selected_img_{i}", 'src') for i in range(4)],
    
    prevent_initial_call=True,
)

def changing_image_selected_product(*args):
    images = args[4:]
    
    # Dictionary mapping trigger IDs to corresponding image indices
    trigger_to_index = {f"selected_img_{i}": i for i in range(4)}

    # Find the index of the triggered element
    triggered_index = trigger_to_index.get(ctx.triggered_id, None)

    if triggered_index is not None:
        return images[triggered_index]
    else:
        return dash.no_update

@app.callback(
    Output("graph_products_img", 'figure', allow_duplicate=True),
    
    Input('dropdown_nutrients_img', 'value'),
    Input('check_list_graph_img','value'),
    
    State('pnns1_chosen', 'data'),
    State('pnns2_chosen', 'data'),
    State('dropdown_country','value'),
    
    State('personnalized_sorting', 'data'),
    State('sliced_file', 'data'),
    State("dropdown_diet", "value"), 
    State('search_on', 'data'),
    State('dropdown_number_product', 'value'),
    
    prevent_initial_call=True,
)
# When modifying the graphic
def modifying_graph(nutrients_choice, ch_list_graph, pnns1_chosen, pnns2_chosen, country, 
                    selected_diet, df_slice, dropdown_diet, search_on, n_best):
    elapsed_time = time.time() if DEBUG else None
    if search_on:
        df = pd.read_json(StringIO(df_slice), orient='split')         
        df_N_best = df_sorting(dropdown_diet, df).head(n_best)
    else:
        df = return_df(country, pnns1_chosen, pnns2_chosen)
        df_N_best = df_sorting(selected_diet, df).head(n_best)

    figure = create_figure_products(df, nutrients, nutrients_choice, ch_list_graph, df_N_best)
    
    print("modifying_graph: ", time.time() - elapsed_time) if DEBUG else None 
    
    return figure

@app.callback(
    Output('arrow_button_panel', 'children'),
    Output('left_panel', 'style'),
    Output('left_panel_div2', 'style'),
    
    Input('arrow_button_panel', 'n_clicks'),
    
    prevent_initial_call=True,
)
def left_panel_display(n_clicks):
    # To display or not the left panel
    if n_clicks%2:
        style_panel={'background-color': '#F0F0F0', 'overflowY': 'scroll', 'height': '100vh', 'flex': '0.1', 'direction': 'ltr',
             'border-right': '1px solid black', 'margin':'0px'}
        style_panel_div={'display':'None'}
        #Unicode: U+2261 or html &#8801;
        return "≡", style_panel, style_panel_div 
    
    else:
        style_panel={'background-color': '#F0F0F0', 'overflowY': 'scroll', 'height': '100vh', 'flex': '1', 'direction': 'rtl',
             'border-right': '1px solid black', 'margin':'0px'}
        style_panel_div={'display':'block'}
        
        return "←", style_panel, style_panel_div
    
@app.callback(
    Output('images_gestion', 'style', allow_duplicate=True),
    Output('browser_history_div', 'style'),
    Output('browser_table', 'data'),
    Output('browser_table', 'columns'),
    Output('browser_table', 'selected_rows'),
    Output('dropdown_country','value', allow_duplicate=True),
    Output('pnns1_chosen','data', allow_duplicate=True),
    Output('pnns2_chosen','data', allow_duplicate=True),
    Output('loading_history','data'),
    Output('search_bar', 'value'),
    *[Output(f'{diet}_div', 'n_clicks') for diet in diets],
    
    Input('browsing_button','n_clicks'),
    Input('browser_table', 'selected_rows'),
    
    State('history', 'data'),
    State('dropdown_country', 'value'),
    State('type_search_product', 'value'),
    
    prevent_initial_call=True,
)

def browsing_history(clicks, selected_rows, history_nav, country, type_search_product):
    elapsed_time = time.time() if DEBUG else None
    
    pnns1, pnns2, loading_history, search_bar = dash.no_update, dash.no_update, dash.no_update, dash.no_update
    columns, df_history_nav = dash.no_update, dash.no_update
    clicks_diet = [dash.no_update] * len(diets)
    
    if ctx.triggered_id == "browsing_button":
        
        style_images_gestion = {'display':'None'}
        style_browser_history = {'display':'block'}
        selected_rows = []
        country = dash.no_update
        
        # transforming to Dataframe
        df_history_nav = pd.DataFrame(history_nav, columns = ["Type", "Country", "Pnns1", "Pnns2", "Diet", "Code"])

        columns=[{'name': col, 'id': col} for col in df_history_nav.columns]
        
        # I don't show the code
        df_history_nav=df_history_nav.to_dict('records')
        
    elif ctx.triggered_id == "browser_table":
        
        # We retrieve the row and it's data
        selected_history = history_nav[selected_rows[0]]
        
        # We modify the country, if the actual setup is not the same
        if selected_history[1] == country:
            country = dash.no_update
        else: 
            country = selected_history[1]
        
        if "Product:" in selected_history[0]:
            # We check the type of data currently selected
            if type_search_product == "Product name":
                # We eliminate "product: " to conserve the name of the product
                search_bar = selected_history[0].lstrip('Product: ')
            elif type_search_product == "Product code":
                search_bar = selected_history[5]
                
        elif "Navigation" in selected_history[0]:
            
            pnns1, pnns2, diet_choice = selected_history[2], selected_history[3], selected_history[4]
            
            # To signal a modification and help reload pnns button from left panel
            loading_history = True
            
            if diet_choice != None:
                
                # We modify the dash.component to trigger a diet like search
                diet_index = diets.index(diet_choice) if diet_choice in diets else None
                if diet_index is not None:
                    clicks_diet[diet_index] = 1
        
        style_images_gestion = {'display': 'block', 'flex-direction': 'row', 'width': '100%'}
        style_browser_history = {'display':'None'}            
            
    output_values = [style_images_gestion, style_browser_history, df_history_nav, columns, selected_rows, country, pnns1, pnns2, loading_history, search_bar, *clicks_diet]
    
    print("browsing_history", time.time() - elapsed_time) if DEBUG else None  
    return tuple(output_values)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
    