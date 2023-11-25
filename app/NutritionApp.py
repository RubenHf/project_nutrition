import dash
from dash import Dash, html, dcc, Output, Input, State, ctx
import pandas as pd
import math
from io import StringIO
import time

# Importing the functions
from app.dash_figures import create_figure_products
from app.dash_components import generate_slider, generate_dropdown
from app.data_handling import pnns_groups_options, return_df, get_image, get_code, mapping_nutriscore_IMG, df_sorting
from app.data_handling import get_data, products_by_countries,get_pnns_groups_1, get_pnns_groups_2, get_pnns_groups

##### Initialize the app - incorporate css
# Linked to the external CSS file 
# For display depending of screen
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', '/assets/styles.css']

app = Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)

server = app.server

app.title = 'Nutrition app'

versionning = "version: 0.6.3"

DEBUG = True

products_availability = "Referenced products: " + str(get_data().shape[0])

nutrients = ["fat_100g", "saturated-fat_100g", "carbohydrates_100g", "fiber_100g", "proteins_100g", "salt_100g", "macronutrients_100g"]

slider_trigger = ["slider_energy", "slider_fat", "slider_saturated", "slider_carbohydrates", "slider_fiber", "slider_proteins", "slider_salt", "slider_macronutrients"]

diets = ["Healthier foods", "Low sugar foods", "Protein rich foods", "Energy rich foods", "Low fat foods"]

# Default setup
default_country, default_pnns1, default_pnns2, default_diet = "France", "Fruits and vegetables", "Soups", "Healthier foods" 
default_graphic_option = "Distribution"

# Generate list of unique countries and number of products
unique_countries = products_by_countries()

# Generate pnns_groups 1 and 2, and sorted
pnns_groups_1 = get_pnns_groups_1()

pnns_groups_2 = get_pnns_groups_2()

pnns_groups = get_pnns_groups()

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

                # Dropdown for the countries
            html.Div([
                generate_dropdown(default_country, unique_countries, "Choose a country", False, 'dropdown_country', False)
            ], style={'margin': '0 auto', 'border': '1px solid black'}),

            # Searchbar products
            html.Div([
                generate_dropdown(None, [], "Search a product", False, 'search_bar')
            ], style={'margin': '0 auto', 'border': '1px solid black'}),

            # Advanced searchbar products
            html.Div([
                html.Button(
                        "Advanced search 🔍",
                        id="advanced_search_button",
                        n_clicks=0,
                        style={'align-items': 'center', 'justify-content': 'center', 'border': '1px solid black',
                            'font-size': '15px', 'color': 'black', 'width': '100%', 
                               'textAlign': 'center', 'margin': '0px', 'background-color': 'white'}
                    )
            ], style={'margin': '0 auto', 'margin-bottom': '20px'}),

            html.Div([
                html.Div([
                    html.Button(
                        pnns1["label"],
                        id=str(pnns1["value"]),
                        n_clicks=0,
                        style={'font-size': '16px', 'color': 'black', 'width': '100%', 
                               'textAlign': 'left', 'margin': '0px', 'border': 'none', 'background-color': 'gray'}
                    ),
                    html.Button(
                        pnns2["label"],
                        id=str(pnns2["value"]),
                        n_clicks=0,
                        style={'font-size': '10px', 'color': 'black', 'width': '100%', 'display':'none',
                               'textAlign': 'left', 'margin': '0px', 'border': 'none', 'background-color': 'gray'}
                    ),
                ], style={'display': 'flex', 'flex-direction': 'column', 'width': '100%'}) 
                if y == 0 and str(pnns1["value"]) != str(pnns2["value"]) else 
                html.Button(
                        pnns1["label"],
                        id=str(pnns1["value"]),
                        n_clicks=0,
                        style={'font-size': '16px', 'color': 'black', 'width': '100%', 
                               'textAlign': 'left', 'margin': '0px', 'border': 'none', 'background-color': 'gray'}
                    )
                if str(pnns1["value"]) == str(pnns2["value"]) else
                html.Div([
                    html.Button(
                        pnns2["label"],
                        id=str(pnns2["value"]),
                        n_clicks=0,
                        style={'font-size': '10px', 'color': 'black', 'width': '100%', 'display':'none', 
                               'textAlign': 'left', 'margin': '0px', 'border': 'none', 'background-color': 'gray'}
                    ),
                ])
                for pnns1 in pnns_groups_options(default_country, "pnns_groups_1")
                for y, pnns2 in enumerate(pnns_groups_options(default_country, "pnns_groups_2", pnns1["value"]))
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

        # Section governing the advanced search window
        dcc.Loading(id="loading_section_1", type="default", children=[
            html.Div([
                html.Div([html.Strong("ADVANCED SEARCH")], 
                                     style={'font-size': '24px', 'color': 'black', 'width': '100%', 
                           'textAlign': 'center', 'margin': '0px', 'border': 'none', 'background-color': 'gray',
                                           'display': 'flex', 'flex-direction': 'column', 'width': '100%'}),
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
                    html.Button(html.Strong("Reset"), id="reset_sliders_button", n_clicks=0)
                ], style={'float': 'center', 'margin':'0 auto', 'textAlign': 'center', 'color': 'black', 'fontSize': 15, 'margin-bottom': '20px'}),

                # Button to confirm the search 
                html.Div([
                    html.Button("Search", id="search_confirmation_button", n_clicks=0, style={'width': '200px'}),
                ], style={'float': 'center', 'font-size': '12px', 'color': 'black', 'width': '200px', 'margin':'0 auto', 
                           'textAlign': 'center', 'border': '1px solid black', 'background-color': 'lightgray'}),

                # Horizontale line
                html.Hr(style={'border-top': '4px solid black'}),  
                
            ], id = 'advanced_search_div', style={'float': 'center', 'display': 'None', 'flex-direction': 'row', 
                                              'width': '100%', 'background-color': '#F0F0F0', 'margin-bottom': '20px'}),
        ]),

        
        dcc.Loading(id="loading_section_2", type="default", children=[
            html.Div([

                # To display a selected product at the top

                html.Div(id='selected_product_style', style={'display':'None'}, children=[
                    html.Div(id='selected_product_title',  
                        style={'font-size': '24px', 'color': 'black', 'width': '100%', 
                           'textAlign': 'center', 'margin': '0px', 'border': 'none', 'background-color': 'gray',
                            'display': 'flex', 'flex-direction': 'column', 'width': '100%'}),
                            
                    html.Div([
                        html.Img(id='selected_product_img', src=dash.get_asset_url('no_image.jpg'), 
                            alt="No image available", style = {'height':'450px', 'width':'450px'}),
                        html.Div(id='selected_product_texte')
                    ], style={'flex-direction': 'row', 'width': '100%'})

                ]),

                # To display the list of products

                html.Div(id='images_title', 
                                 style={'font-size': '24px', 'color': 'black', 'width': '100%', 
                       'textAlign': 'center', 'margin': '0px', 'border': 'none', 'background-color': 'gray',
                                           'display': 'flex', 'flex-direction': 'column', 'width': '100%'}),

                html.Div([
                    html.Div([
                        html.Button(children=f"{diet}", id=f"{diet}_div", n_clicks=0,
                                    style={'font-size': '16px', 'color': 'black', 'textAlign': 'left', 'margin': '0px',
                                           'border': '1px', 'background-color': 'lightgray', 'width': '100%', 'margin': 'auto'}),
                        html.Div([
                            html.Div([
                                # dcc.Link for having the clickable action on
                                dcc.Link( 
                                    html.Img(id=f"{diet}_img_{i}", src=dash.get_asset_url('no_image.jpg'), n_clicks = 0,
                                         alt="No image available", style={'height': '200px', 'width': '200px'}),
                                href=''),
                                html.Div(id=f"{diet}_div_{i}")
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
                        dcc.RadioItems(
                            value=default_graphic_option,
                            options=[
                                {'label': label, 'value': label} 
                                for label in ['Radarplot', 'Distribution', 'Products']
                            ],
                            inline=True,
                            id='check_list_graph_img',
                            style={'textAlign': 'center', 'color': 'black', 'fontSize': 15, 'width': '100%'}
                        )
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


            ], style={'display': 'block', 'flex-direction': 'row', 'width': '100%'},  id='images_gestion')
        ]),

            
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
    Output('dropdown_country','value'),
    
    Input('dropdown_country','value'),
    prevent_initial_call=True,
)

# We define the countries list
def choice_country(country):
    
    if country == []:
        country = None
        
    return country
    
@app.callback(
    Output('search_bar', 'options'),
    
    Input('dropdown_country','value'),
)

# We prepare the search_bar, changing when the country choice is different
def search_bar_option_def(country):#, pnns1_chosen, pnns2_chosen):    
    
    elapsed_time = time.time() if DEBUG else None
    
    # If we change pnns or country group, we change the bar_option
    df = return_df(country, None, None)

    # Get a Series with unique product names and their counts
    unique_counts = df['product_name'].value_counts()
    # Sort the unique product names
    sorted_names = unique_counts.index.sort_values()

    # Create the search_bar_option list
    search_bar_option = [
        {
            'label': f"{name} [{count} products]",
            'value': name
        }
        for name, count in unique_counts[sorted_names].items()
    ]
    
    print("search_bar_option_def", time.time() - elapsed_time) if DEBUG else None
    return search_bar_option


@app.callback(
    *[Output(f'{pnns2}', 'style') for pnns2 in pnns_groups_2],
    *[Output(f'{pnns1}', 'children') for pnns1 in pnns_groups_1],
    *[Output(f'{pnns2}', 'children') for pnns2 in pnns_groups_2],
    Output("advanced_search_div", 'style', allow_duplicate=True),
    Output('pnns1_chosen', 'data'),
    Output('pnns2_chosen', 'data'),
    
    *[Input(f'{pnns1}', 'n_clicks') for pnns1 in pnns_groups_1],
    *[Input(f'{pnns2}', 'n_clicks') for pnns2 in pnns_groups_2],
    Input('dropdown_country','value'),
    
    prevent_initial_call=True,
)
def click_pnns_showing(*args):
    elapsed_time = time.time() if DEBUG else None
    output_values = []
    visible = {'font-size': '10px', 'color': 'black', 'width': '100%', 'display':'block', 
              'textAlign': 'left', 'margin': '0px', 'border': 'none', 'background-color':'#C5C5C5'}
    
    clicked_on = {'font-size': '16px', 'color': 'black', 'width': '100%', 'display':'block', 
              'textAlign': 'left', 'margin': '0px', 'border': 'none', 'background-color':'#C5C5C5'}
    
    style_search_div = {'display': 'None'}
    
    # We retrieve the last argument,  that will be the country
    country = args[-1]
    # When a pnns_groups_1 was clicked on
    if ctx.triggered_id in pnns_groups_1:
        pnns1_chosen = ctx.triggered_id
        pnns2_chosen = None
        
        for pnns1 in pnns_groups_1:
            if pnns1 in ['unknown', 'Alcoholic beverages']:
                continue
            for pnns2 in pnns_groups[pnns1]:
                if pnns1 == pnns2:
                    continue
                if ctx.triggered_id == pnns1:
                    output_values.append(visible)
                else:
                    output_values.append({'display': 'none'})
        
        print("click_pnns_showing_1", time.time() - elapsed_time) if DEBUG else None
    
    # When a pnns_groups_2 was clicked on
    elif ctx.triggered_id in pnns_groups_2:
        pnns1_chosen = dash.no_update
        pnns2_chosen = ctx.triggered_id
        
        for pnns1 in pnns_groups_1:
            for pnns2 in pnns_groups[pnns1]:
                if pnns1 == pnns2:
                    continue
                
                # It helps to modify back the others ones clicked before
                if ctx.triggered_id in pnns_groups[pnns1]:
                    if ctx.triggered_id == pnns2:
                        output_values.append(clicked_on)
                    else:
                        output_values.append(visible)
                else: 
                    output_values.append(dash.no_update)  
        print("click_pnns_showing_2", time.time() - elapsed_time) if DEBUG else None        
    
    # The country was change, we are modifying the title
    if ctx.triggered_id == 'dropdown_country': 
        pnns1_chosen = None
        pnns2_chosen = None
        for pnns2 in pnns_groups_2:
            output_values.append(dash.no_update)
        
        pnns_groups_1_options = pnns_groups_options(country, "pnns_groups_1")
        
        for pnns1 in pnns_groups_1_options:
            output_values.append(pnns1["label"])

        for pnns1 in pnns_groups_1_options:
            for pnns2 in pnns_groups_options(country, "pnns_groups_2", pnns1["value"]):
                if str(pnns1["value"]) != str(pnns2["value"]):
                    output_values.append(pnns2["label"])
        print("click_pnns_showing_3", time.time() - elapsed_time) if DEBUG else None

    else:
        for pnns1 in pnns_groups_1:
            if pnns1 in pnns_groups:
                for y, pnns2 in enumerate(pnns_groups[pnns1]):
                    if y == 0 and pnns1 != pnns2:
                        output_values.append(dash.no_update)
                        output_values.append(dash.no_update)

                    else: 
                        output_values.append(dash.no_update)
        print("click_pnns_showing_4", time.time() - elapsed_time) if DEBUG else None
    
    print("click_pnns_showing", time.time() - elapsed_time) if DEBUG else None
    
    output_values.append(style_search_div)
    output_values.append(pnns1_chosen)
    output_values.append(pnns2_chosen)
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

@app.callback(
    Output('images_title', 'children'),
    *[Output(f'{diet}_div', 'children') for diet in diets],
    *[Output(f'{diet}_img_{i}', 'src') for diet in diets for i in range(20)],
    *[Output(f'{diet}_img_{i}', 'style') for diet in diets for i in range(20)],
    *[Output(f'{diet}_div_{i}', 'children') for diet in diets for i in range(20)],
    Output("graph_products_img", 'figure'),
    Output("graphic_gestion", 'style'),
    Output('personnalized_sorting', 'data', allow_duplicate=True),
    Output("selected_product_style", 'style'),
    Output("selected_product_img", 'src'),
    Output("selected_product_title", 'children'),
    Output("selected_product_texte", 'children'),
    Output('advanced_search_div', 'style', allow_duplicate=True),
    Output('search_on', 'data'),
    Output('shown_img', 'data'),
    
    *[Input(f'{diet}_div', 'n_clicks') for diet in diets],
    *[Input(f'{diet}_img_{i}', 'n_clicks') for diet in diets for i in range(20)],
    Input('pnns1_chosen', 'data'),
    Input('pnns2_chosen', 'data'),
    Input('dropdown_country','value'),
    Input('dropdown_nutrients_img', 'value'),
    Input('check_list_graph_img','value'),
    Input('search_bar', 'value'),
    Input('search_confirmation_button', 'n_clicks'),
    Input('advanced_search_button', 'n_clicks'),
    
    State('personnalized_sorting', 'data'),
    State('sliced_file', 'data'),
    State("dropdown_diet", "value"), 
    State('search_on', 'data'),
    State('dropdown_number_product', 'value'),
    State('shown_img', 'data'),
    
    prevent_initial_call=True,
)

def display_images(*args):
    elapsed_time = time.time() if DEBUG else None
    
    # A way to handle that many variables
    diet1, diet2, diet3, diet4, diet5,  = args[0], args[1], args[2], args[3], args[4]
    list_clicks_img = args[5:-14]
    pnns1_chosen, pnns2_chosen, country = args[-14], args[-13], args[-12]
    nutrients_choice, ch_list_graph, search_bar = args[-11], args[-10], args[-9]
    clicked_search, click_advanced_search = args[-8], args[-7]
    selected_diet, df_slice, dropdown_diet, search_on, n_best = args[-6], args[-5], args[-4], args[-3], args[-2]
    shown_img_data = args[-1] 

    output_values = []
    title = None
    figure = dash.no_update
    selected_product_img = dash.no_update
    selected_product_title = dash.no_update
    selected_product_texte = dash.no_update
    selected_product_style = dash.no_update
    advanced_search_style = dash.no_update
    
    if ctx.triggered_id in ['check_list_graph_img', 'dropdown_nutrients_img']:
        images = [dash.no_update] * 100
        styles_images = [dash.no_update] * 100
        textes_images = [dash.no_update] * 100
        subtitles = [dash.no_update] * 5
    else: 
        images, textes_images, styles_images, subtitles = [], [], [], []
    
    # dataframe preparation, only when necessary
    if ctx.triggered_id not in ['advanced_search_button', 'search_confirmation_button']:
        df = return_df(country, pnns1_chosen, pnns2_chosen)
        
    elif ctx.triggered_id == 'search_confirmation_button':
        df = pd.read_json(StringIO(df_slice), orient='split')
        
    # If clicking on diet preference or confirmed search
    if ctx.triggered_id in [f'{diet}_div' for diet in diets] + ['search_confirmation_button']:      
        for i, diet in enumerate([diet + "_div" for diet in diets]):
            subtitles.append(html.Strong(f"{diets[i]}"))
            
            if ctx.triggered_id in ['search_confirmation_button', diet]: 
                if ctx.triggered_id == 'search_confirmation_button':
                    if diet[:-4] == dropdown_diet:
                        selected_diet = diets[i] # To keep the selected button
                        advanced_search_style = dash.no_update
                        search_on = True
                    else: 
                        selected_diet = None

                else:
                    # Add information when it is the selected diet
                    if diet == ctx.triggered_id:
                        search_on = False
                        selected_diet = diets[i] # To keep the selected button
                        advanced_search_style = {'display':'None'}
                    else: 
                        selected_diet = None
                
                if selected_diet != None:
                    # sort and retrieve the N best, then match the nutriscore image           
                    df_N_best = df_sorting(diets[i], df).head(n_best)
                    df_N_best = mapping_nutriscore_IMG(df_N_best)

                    title = html.Strong(f"BEST RECOMMENDED PRODUCTS FOR {diets[i].upper()}")


                    for _, row in df_N_best.iterrows():

                        images.append(get_image(str(row.iloc[0])))
                        styles_images.append({'width': '350px', 'height': '350px'})

                        textes_images.append(
                            html.Div([
                                html.Img(
                                src=dash.get_asset_url(str(row.iloc[-1])),
                                    alt="Product Nutriscore",
                                    style={'width': '100px', 'height': '50px', 'margin-left':'10px'}
                                )] + [
                                html.Div([
                                    html.Strong(f"{col}:"),
                                    f" {row[col]}"],
                                    style={'text-align': 'left', 'margin-top': '1px', 'margin-left':'10px'}
                                )
                                for col in row.index[:-1]  # Exclude the last column (nutriscore_image)
                            ], style={'display': 'flex', 'flex-direction': 'column', 'width': '100%'}))

                    # We complete
                    if df_N_best.shape[0] < 20:
                        images = images + [None] * (20 - df_N_best.shape[0])
                        styles_images = styles_images + [{'display':'None'}] * (20 - df_N_best.shape[0])
                        textes_images = textes_images + [None] * (20 - df_N_best.shape[0])
                else: 
                    images = images + [None] * 20
                    styles_images = styles_images + [{'display':'None'}] * 20
                    textes_images = textes_images + [None] * 20
                
            # Add blanks when it is not the selected one
            else:

                images = images + [None] * 20
                styles_images = styles_images + [{'display':'None'}] * 20
                textes_images = textes_images + [None] * 20
        
        # Creating a figure of the data distribution 
        figure = create_figure_products(df, nutrients, nutrients_choice, ch_list_graph, df_N_best)
        graphic_gestion_style = {'display':'block'}
        selected_product_style = {'display':'None'}
        
    # When navigating on the left panel    
    elif ctx.triggered_id in ['pnns1_chosen', 'pnns2_chosen', 'dropdown_country']:
        
        title = html.Strong("BEST RECOMMENDED PRODUCTS BY CATEGORY")
        figure = dash.no_update
        graphic_gestion_style = {'display':'None'}
        selected_product_style = {'display':'None'}
        advanced_search_style = {'display':'None'}
        selected_diet = dash.no_update
        search_on = False
        
        # df is sorted, n firsts images shown
        for diet in diets:
            
            subtitles.append(html.Strong(f"{diet}"))
            df_N_best = df_sorting(diet, df).head(n_best)
            df_N_best = mapping_nutriscore_IMG(df_N_best)
            
            for _, IMG in df_N_best.iterrows():
                code = IMG.iloc[0]
                product_name = IMG.iloc[1]
                images.append(get_image(str(code)))
                styles_images.append({'width': '150px', 'height': '150px'})

                textes_images.append(
                    html.Div([
                        html.Img(
                        src=dash.get_asset_url(str(IMG.iloc[-1])),
                            alt="Product Nutriscore",
                            style={'width': '100px', 'height': '50px', 'margin-left':'10px'}
                        ),
                    ] + [
                    html.Div(product_name, style={'text-align': 'center', 'margin-top': '5px'}) 
                    ])
                )
            # We complete
            if df_N_best.shape[0] < 20:
                images = images + [None] * (20 - df_N_best.shape[0])
                styles_images = styles_images + [{'display':'None'}] * (20 - df_N_best.shape[0])
                textes_images = textes_images + [None] * (20 - df_N_best.shape[0])
                
    # When modifying the graphic
    elif ctx.triggered_id in ['check_list_graph_img', 'dropdown_nutrients_img']:

        if search_on:
            df = pd.read_json(StringIO(df_slice), orient='split')         
            df_N_best = df_sorting(dropdown_diet, df).head(n_best)
        else:
            df_N_best = df_sorting(selected_diet, df).head(n_best)
        
        figure = create_figure_products(df, nutrients, nutrients_choice, ch_list_graph, df_N_best)
        selected_diet, graphic_gestion_style = dash.no_update, dash.no_update
        images = [dash.no_update] * 100
        styles_images = [dash.no_update] * 100
        textes_images = [dash.no_update] * 100
        subtitles = [dash.no_update] * 5
        
        
    elif ctx.triggered_id in ["search_bar"] + [f'{diet}_img_{i}' for diet in diets for i in range(20)]:
        try:
            if ctx.triggered_id == "search_bar":
                df_product = get_data().query('product_name == @search_bar')

            else: 
                #shown_img_data[ctx.triggered_id]
                url = shown_img_data[ctx.triggered_id]
                code = get_code(url)
                df_product = get_data().query('code == @code')

            # We search for the product [Only one for now]
            df_product = df_product.head(1) if df_product.shape[0] > 1 else df_product
            df_product = mapping_nutriscore_IMG(df_product)

            selected_product_img = get_image(str(df_product["code"].values[0]))
            selected_product_title = html.Strong(f"{df_product['product_name'].values[0]}")
            selected_product_texte = html.Div([
                html.Div(
                    [
                    html.Img(
                    src=dash.get_asset_url(str(df_product["nutriscore_score_letter"].values[0])),
                        alt="Product Nutriscore",
                        style={'width': '100px', 'height': '50px', 'margin-left':'10px'}
                    ),
                ], style={'display': 'flex', 'flex-direction': 'column', 'width': '100%'}
                + 
                [
                    html.Strong(f"{col}:"),
                    f" {df_product[col].values[0]}"],
                    style={'text-align': 'left', 'margin-top': '1px', 'margin-left':'10px'}
                )
                for col in df_product.columns[:-1]  # Exclude the last column (nutriscore_image)
                ])

            pnns1 = df_product["pnns_groups_1"].values[0]
            pnns2 = df_product["pnns_groups_2"].values[0]
            
        except:
            pnns1, pnns2 = None, None
            selected_product_img = dash.get_asset_url("no_image.jpg")
            selected_product_title = html.Strong("Product not found, search for another one")
            selected_product_texte = html.Strong("Product not found, search for another one")
                
        df = return_df(country, pnns1, pnns2).copy()
        
        title = html.Strong("BEST RECOMMENDED PRODUCTS BY CATEGORY")
        # df is sorted, n firsts images shown
        for diet in diets:
            
            subtitles.append(html.Strong(f"{diet}"))
            
            df_N_best = df_sorting(diet, df).head(n_best)
            df_N_best = mapping_nutriscore_IMG(df_N_best)
            
            for _, IMG in df_N_best.iterrows():
                code = IMG.iloc[0]
                product_name = IMG.iloc[1]
                images.append(get_image(str(code)))
                styles_images.append({'width': '150px', 'height': '150px'})

                textes_images.append(
                    html.Div([
                        html.Img(
                        src=dash.get_asset_url(str(IMG.iloc[-1])),
                            alt="Product Nutriscore",
                            style={'width': '100px', 'height': '50px', 'margin-left':'10px'}),
                    ] + [
                    html.Div(product_name, style={'text-align': 'center', 'margin-top': '5px'})
                    ])
                )
                
            # We complete
            if df_N_best.shape[0] < 20:
                images = images + [None] * (20 - df_N_best.shape[0])
                styles_images = styles_images + [{'display':'None'}] * (20 - df_N_best.shape[0])
                textes_images = textes_images + [None] * (20 - df_N_best.shape[0])
                
        # Creating a figure of the data distribution 
        figure = create_figure_products(df, nutrients, nutrients_choice, ch_list_graph, df_product)
        graphic_gestion_style = {'display':'block'}
        selected_product_style = {'display':'block'}
        advanced_search_style = {'display':'None'}
        search_on = False
        
    elif ctx.triggered_id == 'advanced_search_button':

        advanced_search_style = {'float': 'center', 'display': 'block', 'flex-direction': 'row', 
                                'width': '100%', 'background-color': '#F0F0F0', 'margin-bottom': '20px'}
        graphic_gestion_style = {'display':'None'}
        selected_product_style = {'display':'None'}
        search_on = False
        
        images = [None] * 100
        styles_images = [{'display':'None'}] * 100
        textes_images = [None] * 100
        subtitles = [None] * 5

    output_values = [title, *subtitles, *images, *styles_images, *textes_images, 
                     figure, graphic_gestion_style, selected_diet, selected_product_style, 
                     selected_product_img, selected_product_title, selected_product_texte,
                     advanced_search_style, search_on, shown_img_data]

    # Top keep tract of the images src to load when clicking on 
    for i, src in enumerate(images):
        key = f'{diets[int(i/20)]}_img_{i%20}'
        if src == dash.no_update or src == None:
            continue
        else:
            shown_img_data[key] = src
            
    print("display_images", time.time() - elapsed_time) if DEBUG else None    
    return tuple(output_values)

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
        style_panel={'background-color': '#F0F0F0', 'overflowY': 'scroll', 'height': '100vh', 'flex': '0.1', 'direction': 'rtl',
             'border-right': '1px solid black', 'margin':'0px'}
        style_panel_div={'display':'None'}
        
        return "→", style_panel, style_panel_div 
    
    else:
        style_panel={'background-color': '#F0F0F0', 'overflowY': 'scroll', 'height': '100vh', 'flex': '1', 'direction': 'rtl',
             'border-right': '1px solid black', 'margin':'0px'}
        style_panel_div={'display':'block'}
        
        return "←", style_panel, style_panel_div
    

# Run the app
if __name__ == '__main__':
    app.run(debug=False)
    