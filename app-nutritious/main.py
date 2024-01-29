import dash
from dash import Dash, html, Output, Input, State, ctx, Patch, DiskcacheManager, CeleryManager
from dash.exceptions import PreventUpdate
import pandas as pd
import requests
import math
import numpy as np
from io import StringIO
import time
from collections import Counter 

# Importing the functions
from functions.dash_figures import create_figure_products, patch_graphic, figure_result_model
from functions.data_handling import pnns_groups_options, return_df, get_code, df_sorting, get_nutriscore_image
from functions.data_handling import generate_texte_image, get_texte_product, get_data
from functions.display_images import *
from functions.language import get_languages_options
from frontend.navigation_panel import generating_navigating_panel
from frontend.navigation_result import generating_navigation_result
from config_store import generating_dcc_store
from frontend.style import return_style16_nd
# We import the initials values
from config import *


# Linked to the external CSS file 

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', '/assets/styles.css']

app = Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)

server = app.server

app.title = 'Nutritious app'

versionning = "0.7.2"

DEBUG = False

if 'REDIS_URL' in os.environ:
    # Use Redis & Celery if REDIS_URL set as an env variable
    from celery import Celery
    celery_app = Celery(__name__, broker=os.environ['REDIS_URL'], backend=os.environ['REDIS_URL'])
    background_callback_manager = CeleryManager(celery_app)

else:
    # Diskcache for non-production apps when developing locally
    import diskcache
    cache = diskcache.Cache("./cache")
    background_callback_manager = DiskcacheManager(cache)

# Front-end of the app
app.layout = html.Div([
    # Function generating the left Frontside of the app
    generating_navigating_panel(option_languages, translations[initial_language], initial_language, unique_countries, pnns_groups_1, pnns_groups_2, pnns_groups, products_availability, versionning),

    # Function generating the right Frontside of the app
    generating_navigation_result(translations[initial_language], initial_language, pnns_groups_1, pnns_groups_2, pnns_groups, diets, nutrients),
    
    # Function generating the dcc_store components, we return a tuple, so we need to unpack
    *generating_dcc_store(diets, initial_language),

    # Dummy var
    html.Div(id='dummy_output', style={'display': 'none'})
    
],id='app-container', style={'justify-content': 'space-between', 'margin': '0', 'padding': '0'})

# When the user changes the language
@app.callback(
    Output('language_user', 'data'),
    Output('dropdown_number_product', 'options'),
    Output('type_search_product', 'options'),
    Output('dropdown_language', 'options'),
    Output('picture_search_button', 'children'),
    Output('advanced_search_button', 'children'),
    Output('browsing_button', 'children'),
    Output('search_bar', 'placeholder'),
    Output('referencing', 'children'),
    #Output('images_title', 'children', allow_duplicate=True),
    *[Output(f'{diet}_div', 'children', allow_duplicate=True) for diet in diets],
    Output('top_button_graphic', 'children'),
    Output('bottom_button_graphic', 'children'),
    
    Input('dropdown_language', 'value'),

    #State('images_title', 'children'),
    
    prevent_initial_call=True,
    )
def definition_language_user(input_language):

    elapsed_time = time.time() if DEBUG else None

    # Changing language of display items options
    options_display=[
        {'label': translations[input_language][f'displaying_{n}_products'], 'value': n}
                    for n in [5, 10, 15, 20]
                ]
    # Changing language of options radio items
    options_type_search = [
            {'label': translations[input_language]['product_name'], 'value': 'product_name'}, 
            {'label': translations[input_language]['product_code'], 'value': 'product_code'} 
        ]
    # Changing the language of the sentence in language options
    options_language = get_languages_options(translations[input_language])

    children_picture_search = translations[input_language]['picture_search_beta']
    children_advanced_search = translations[input_language]['advanced_search']
    children_browsing_search = translations[input_language]['browsing_history']
    place_holder_search = translations[input_language]['search_product']
    children_referencing = f"{translations[input_language]['referenced_products']}: {products_availability}"
    output_subtitles = [translations[input_language][diet] for diet in diets]
    children_top_graph_button = translations[input_language]['Show the distribution of the product']
    children_bottom_graph_button = translations[input_language]['Show the distribution of the products']

    print("Language_user", time.time() - elapsed_time) if DEBUG else None

    return (input_language, options_display, options_type_search, options_language, 
            children_picture_search, children_advanced_search,children_browsing_search, 
            place_holder_search, children_referencing, *output_subtitles, children_top_graph_button, children_bottom_graph_button)

@app.callback(
    Output('sliced_file', 'data'),
    
    Input('dropdown_country','value'),
    Input('dropdown_pnns1','value'),
    Input('dropdown_pnns2','value'),
    
    Input('advanced_search_button', 'n_clicks'),

    *[Input(f'{slide}', 'value') for slide in slider_trigger],
    
    prevent_initial_call=True,
)

def data_slicing(country, pnns1_chosen, pnns2_chosen, _, 
                 slide_energy, slide_fat, slide_sat_fat, slide_carbs, 
                 slide_fiber, slide_prot, slide_salt, slide_macro):

    sliders = [slide_energy, slide_fat, slide_sat_fat, slide_carbs, slide_fiber, slide_prot, slide_salt, slide_macro]
    elapsed_time = time.time() if DEBUG else None
      
    # Returning no data to show
    if country is None:
        return None

    # It follow the same path for all
    df = return_df(country, pnns1_chosen, pnns2_chosen)
    
    if ctx.triggered_id in slider_trigger:
        for nutrient, slide in zip(["energy_100g"] + nutrients, sliders):
            df = df[(df[nutrient] >= slide[0]) & (df[nutrient] <= slide[1])]
    
    # Transform to json format
    df = df.to_json(orient='split')
    
    print("Data slicing", time.time() - elapsed_time) if DEBUG else None
    return df

    
@app.callback(
    Output('search_bar', 'options'),
    Output('search_bar_data', 'data'),
    
    Input('dropdown_country','value'),
    Input('type_search_product','value'),
    Input('search_bar', 'search_value'), 
    
    State('language_user', 'data'),
    State('search_bar_data', 'data'),
)

# We prepare the search_bar, changing when the country choice is different
def search_bar_option_def(country, dropdown_search, search_bar, language, search_bar_data):
    
    elapsed_time = time.time() if DEBUG else None
    
    if ctx.triggered_id in ['type_search_product', 'dropdown_country'] or search_bar_data is False:
        
        # If we change pnns or country group, we change the bar_option
        df = return_df(country, None, None)
        
        # If we search by product name
        if dropdown_search == 'product_name':
            # Get a Series with unique product names and their counts using Counter
            unique_counts = Counter(df['product_name'])

            # Sort the unique product names
            sorted_names = sorted(unique_counts.keys())

            # Create the search_bar_option list
            search_bar_data = [
                {
                    'label': f"{name} [{count} {translations[language]['products']}]",
                    'value': name
                }
                for name in sorted_names
                for count in [unique_counts[name]]
            ]

        # If we search by product code
        elif dropdown_search == 'product_code':
            # Each product has its own unique code

            # Create the search_bar_option list
            search_bar_data = [
                {
                    'label': code,
                    'value': code
                }
                for code in df['code'].unique()
            ]
            
        search_bar_option = []
    
    # If user has written more than 2 letters or number, we show the selection
    elif ctx.triggered_id == 'search_bar':
        
        if len(search_bar) > 2:
            # We search for the products
            search_bar_option = [
                option for option in search_bar_data
                if search_bar.lower() in str(option['value']).lower()
                ]
        else:
            search_bar_option = dash.no_update 
        
        search_bar_data = dash.no_update    

    print("search_bar_option_def", time.time() - elapsed_time) if DEBUG else None
    return search_bar_option, search_bar_data

@app.callback(
    Output('multiple_product_dropdown', 'value'),
    Output('multiple_product_dropdown', 'options'),
    Output('multiple_product_dropdown', 'style', allow_duplicate=True),
    
    Input('search_bar', 'value'),
    State('language_user', 'data'),
    State('type_search_product', 'value'),
    
    prevent_initial_call=True,
)

# When selected product have multiple possibilities 
def multiple_product_dropdown(search_bar, language, dropdown_search):

    elapsed_time = time.time() if DEBUG else None

    # initialize values
    style_multiple_dropdown = dash.no_update
    option_multiple_dropdown = dash.no_update
    value_multiple_dropdown = None
    
    if dropdown_search == "product_name":
        
        # We search for all the products with the same name
        df_product = get_data().query('product_name == @search_bar')
        
        if df_product.shape[0] > 1:
            # We display the dropdown
            style_multiple_dropdown = {'display':'block'}
            
            # We put the first product
            value_multiple_dropdown = df_product.iloc[0]['code']
            
            # Style for the nutriscore image
            style={'width': '100px', 'height': '25px', 'margin-left':'10px'}
            
            # We put the code as value, as they are unique to each product
            option_multiple_dropdown = [
            {
                'label': html.Div([f"{translations[language]['product_code']}: {row['code']}", 
                                   get_nutriscore_image(row['nutriscore_score_letter'], style)]),
                'value': row['code']
            }
            for _, row in df_product.iterrows()]
        
    print("multiple_product_dropdown", time.time() - elapsed_time) if DEBUG else None        

    return value_multiple_dropdown, option_multiple_dropdown, style_multiple_dropdown 

@app.callback(
    *[Output(f'{pnns2}', 'style') for pnns2 in pnns_groups_2],
    *[Output(f'{pnns1}', 'children') for pnns1 in pnns_groups_1],
    *[Output(f'{pnns2}', 'children') for pnns2 in pnns_groups_2],
    Output('advanced_search_div', 'style', allow_duplicate=True),
    Output('images_gestion', 'style', allow_duplicate=True),
    Output('pnns1_chosen', 'data'),
    Output('pnns2_chosen', 'data'),
    Output('history', 'data', allow_duplicate=True),
    
    *[Input(f'{pnns1}', 'n_clicks') for pnns1 in pnns_groups_1],
    *[Input(f'{pnns2}', 'n_clicks') for pnns2 in pnns_groups_2],
    Input('loading_history','data'),
    Input('dropdown_country','value'),
    Input('pnns1_chosen', 'data'),
    Input('pnns2_chosen', 'data'),
    Input('language_user', 'data'),
    
    State('history', 'data'),

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
    (country, pnns1_chosen, pnns2_chosen, language, history_nav) = args[-5:]
    
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
        
    # Function returning labels of pnns groups 1 and 2
    def return_pnns_label():
        # Product calcul
        pnns_groups_1_options = pnns_groups_options(country, "pnns_groups_1", language)
        
        # New label (= new number of products)
        label_pnns1 = [pnns1["label"] for pnns1 in pnns_groups_1_options]
        
        label_pnns2 = [
            pnns2["label"]
            for pnns1 in pnns_groups_1_options
            for pnns2 in pnns_groups_options(country, "pnns_groups_2", language, pnns1["value"])
            if str(pnns1["value"]) != str(pnns2["value"])
        ]
        return label_pnns1, label_pnns2
    
    # When a pnns_groups_1 or 2 was clicked on
    if ctx.triggered_id in pnns_groups_1 + pnns_groups_2:  
        output_style = changing_style_pnns_button(output_style, ctx.triggered_id)
        
    # To modify style when navigating with a selected product
    elif ctx.triggered_id in ["pnns1_chosen", "pnns2_chosen"]:
        if pnns2_chosen != None:
            output_style = changing_style_pnns_button(output_style, pnns2_chosen)
        elif pnns1_chosen != None:
            output_style = changing_style_pnns_button(output_style, pnns1_chosen)
    
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
    elif ctx.triggered_id == 'dropdown_country':
        
        pnns1_chosen, pnns2_chosen = None, None
        
        # We add to the navigation history
        history_nav.insert(0, ["Navigation", country, pnns1_chosen, pnns2_chosen, None, None])
        
        # We actualize the labels
        output_label_pnns1, output_label_pnns2 = return_pnns_label()

    # Language was changed
    elif ctx.triggered_id == 'language_user':
        # We are not modifying those
        history_nav, pnns2_chosen, pnns1_chosen = dash.no_update, dash.no_update, dash.no_update
        style_search_div, style_images_gestion = dash.no_update, dash.no_update
        output_style = [dash.no_update] * len(pnns_groups_2) 

        # We actualize the labels
        output_label_pnns1, output_label_pnns2 = return_pnns_label()

                        
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
    *[Output(f'{diet}_img_{i}', 'style', allow_duplicate=True) for diet in diets for i in range(20)],
    *[Output(f'{diet}_img_{i}', 'src', allow_duplicate=True) for diet in diets for i in range(20)],
    *[Output(f'{diet}_div_{i}', 'children', allow_duplicate=True) for diet in diets for i in range(20)],
    
    *[Input(f'{diet}_div', 'n_clicks') for diet in diets],
    *[Input(f'{diet}_img_{i}', 'n_clicks') for diet in diets for i in range(20)],
    Input('pnns1_chosen', 'data'),
    Input('pnns2_chosen', 'data'),
    Input('dropdown_country','value'),
    Input('search_bar', 'value'),
    Input('search_confirmation_button', 'n_clicks'),
    Input('advanced_search_button', 'n_clicks'),

    State('prevent_update', 'data'),

    prevent_initial_call=True,
)

# We clear the images and textes before updating it. 
def clearing_textes_images(*args):
    elapsed_time = time.time() if DEBUG else None

    if args[-1] != None:
        raise PreventUpdate

    texte_images = [None] * TOTAL_IMAGES
    src_images = [None] * TOTAL_IMAGES
    style_images = [{'display':'None'}] * TOTAL_IMAGES

    print("clearing_textes_images", time.time() - elapsed_time) if DEBUG else None
    return tuple([*style_images, *src_images, *texte_images])

@app.callback(
    Output('images_title', 'children'),
    *[Output(f'{diet}_div', 'children') for diet in diets],
    *[Output(f'{diet}_img_{i}', 'src') for diet in diets for i in range(20)],
    *[Output(f'{diet}_img_{i}', 'style') for diet in diets for i in range(20)],
    *[Output(f'{diet}_div_{i}', 'children') for diet in diets for i in range(20)],
    *[Output(f"selected_img_{i}", 'src') for i in range(4)],
    *[Output(f"selected_img_{i}", 'style') for i in range(4)],
    *[Output(f"graphic_gestion_{pos}", 'style') for pos in ['bottom', 'top']],
    *[Output(f"{pos}_button_graphic", 'style') for pos in ['bottom', 'top']],
    Output('personnalized_sorting', 'data', allow_duplicate=True),
    Output("selected_product_style", 'style'),
    Output("selected_product_img", 'src'),
    Output("selected_product_title", 'children'),
    Output("selected_product_texte", 'children'),
    Output('advanced_search_div', 'style', allow_duplicate=True),
    Output('search_on', 'data'),
    Output('shown_img', 'data'),
    Output('history', 'data', allow_duplicate=True),
    Output('multiple_product_dropdown', 'style', allow_duplicate=True),
    Output('browser_history_div', 'style', allow_duplicate=True),
    Output('prevent_update', 'data'),
    Output('pnns1_chosen', 'data', allow_duplicate=True),
    Output('pnns2_chosen', 'data', allow_duplicate=True),
    Output('picture_search_div', 'style', allow_duplicate=True),
    Output('data_figure', 'data'),
    
    *[Input(f'{diet}_div', 'n_clicks') for diet in diets],
    *[Input(f'{diet}_img_{i}', 'n_clicks') for diet in diets for i in range(20)],
    Input('pnns1_chosen', 'data'),
    Input('pnns2_chosen', 'data'),
    Input('dropdown_country','value'),
    Input('search_bar', 'value'),
    Input('search_confirmation_button', 'n_clicks'),
    Input('advanced_search_button', 'n_clicks'),
    Input('multiple_product_dropdown', 'value'),
    
    State('type_search_product', 'value'),
    State('personnalized_sorting', 'data'),
    State('sliced_file', 'data'),
    State("dropdown_diet", "value"), 
    State('search_on', 'data'),
    State('dropdown_number_product', 'value'),
    State('shown_img', 'data'),
    State('history', 'data'),
    State('prevent_update', 'data'),
    State('input_search_adv', 'value'),
    State('language_user', 'data'),
    State('data_figure', 'data'),
    
    prevent_initial_call=True,
)

def display_images(*args):
    elapsed_time = time.time() if DEBUG else None
    
    # We unpack the args
    (pnns1_chosen, pnns2_chosen, country, search_bar, clicked_search, click_advanced_search, value_multiple_dropdown,
     type_search_product, selected_diet, df_slice, 
     dropdown_diet, search_on, n_best, shown_img_data, history_nav, prevent_update, user_input, language, data_figure) = args[-19:]
    
    # Return true if one of the diet was click.
    # It is helping for the browser history
    
    clicked_diet_ctx = [f'{diet}_div' for diet in diets]
    browser_diet = any(any(keyword in item['prop_id'] for keyword in clicked_diet_ctx) for item in ctx.triggered)
    
    # Initialize 
    no_display = {'display':'None'}
    images, styles_images, textes_images = [dash.no_update] * TOTAL_IMAGES, [no_display] * TOTAL_IMAGES, [None] * TOTAL_IMAGES
    style_top_graph_button, style_bottom_graph_button = no_display, no_display
    others_img, others_img_style = [None] * 4, [no_display] * 4
    subtitles, title = [None] * len(diets), None
    selected_product_img, selected_product_title, selected_product_texte = None, None, None
    graphic_gestion_style_bottom, graphic_gestion_style_top, selected_product_style, advanced_search_style = no_display, no_display, no_display, no_display
    search_on = False if search_on else dash.no_update
    selected_diet = None if selected_diet != None else dash.no_update
    style_multiple_dropdown = no_display
    style_picture_search_div = no_display
    browser_history_style = no_display
    
    # Setting some conditions
    condition_selected_a_product = ctx.triggered_id in ["search_bar", "multiple_product_dropdown"] + [f'{diet}_img_{i}' for diet in diets for i in range(20)]
    condition_selected_diet_search_navigation = (ctx.triggered_id in clicked_diet_ctx + ['search_confirmation_button']) or (browser_diet)
    
    # dataframe preparation, only when necessary
    if ctx.triggered_id not in ['advanced_search_button', 'search_confirmation_button']:
        df = return_df(country, pnns1_chosen, pnns2_chosen)
        
    elif ctx.triggered_id == 'search_confirmation_button':
        df = pd.read_json(StringIO(df_slice), orient='split', dtype={'code': str})
        # We adjust if the user has entered a value
        if user_input is not None:
            df = df.query('product_name.str.contains(@user_input)')
        
    # If clicking on diet preference or confirmed search or from the browser
    if condition_selected_diet_search_navigation: 
        
        for i, diet in enumerate([diet + "_div" for diet in diets]):
            subtitles[i] = html.Strong(f"{translations[language][diets[i]]}")
            
            if (ctx.triggered_id in ['search_confirmation_button', diet]) or browser_diet: 
                
                # If client clicked on the confirmation button of the advanced search
                if ctx.triggered_id == 'search_confirmation_button':
                    # For the selected diet
                    if diet[:-4] == dropdown_diet: #:-4 is to eliminate some text
                        selected_diet = diets[i] # To keep the selected button
                        advanced_search_style = dash.no_update
                        search_on = True
                        
                    # If none selected
                    elif (dropdown_diet == None) or (dropdown_diet == []):
                        selected_diet = "All"
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
                    df_N_best = df_sorting(diets[i], df).head(n_best)
                    
                    for y, (_, row) in enumerate(df_N_best.iterrows()):
                        index = y if i == 0 else (20 * i) + y

                        styles_images[index] = {'height': '400px', 'width': '400px'}
                        
                        # generate the texte below the image
                        textes_images[index] = get_texte_product(row, language)
                        
                        # We retrieve the images_1 urls 
                        images[index] = row["image_1"]
                        
                    # Replace images by default if something failed in retrieving url
                    images = [dash.get_asset_url('no_image.jpg') if url is np.nan else url for url in images]
                    
                    style_bottom_graph_button = {'display':'block', 'color': 'black'}
        
                # When the user doesn't specifie a diet to search on
                elif selected_diet == "All":
                    subtitles, images, styles_images, textes_images = generate_texte_image(df, diets, n_best, 
                                                                               subtitles, images, 
                                                                               styles_images, textes_images,
                                                                               language)

                    # Replace images by default if something failed in retrieving url
                    images = [dash.get_asset_url('no_image.jpg') if url is np.nan else url for url in images]

        prevent_update = None
        
    # When navigating on the left panel    
    elif ctx.triggered_id in ['pnns1_chosen', 'pnns2_chosen', 'dropdown_country']:
        
        title = html.Strong(translations[language]['best_recommended_products'])
        
        subtitles, images, styles_images, textes_images = generate_texte_image(df, diets, n_best, 
                                                                               subtitles, images, 
                                                                               styles_images, textes_images,
                                                                               language)
        
        # Replace images by default if something failed in retrieving url
        images = [dash.get_asset_url('no_image.jpg') if url is np.nan else url for url in images]
        
        prevent_update = pnns2_chosen if ctx.triggered_id == "pnns2_chosen" else None
                                
    # If the client clicked on the search bar or one of the picture
    elif condition_selected_a_product:
        
        try:
            # If searched by the search bar
            if ctx.triggered_id == "search_bar":
                # We check if it is a product name or code entered

                if type_search_product == "product_name":
                    product_code = get_data().query('product_name == @search_bar').get('code')
                    # If more than 1 product
                    if product_code.shape[0] > 1:
                        code = str(value_multiple_dropdown)
                        style_multiple_dropdown = {'display':'block'}
                    else:
                        code = product_code.values[0]

                elif type_search_product == "product_code":
                    code = str(search_bar)

            # If searched by the intra search bar (multiple products with the same name)
            elif ctx.triggered_id == "multiple_product_dropdown":
                # We get the code
                code = str(value_multiple_dropdown)
                style_multiple_dropdown = {'display':'block'}

            # If searched by clicking on image
            else: 
                url = shown_img_data[ctx.triggered_id]
                code = get_code(url)

            # Some of the codes are writen in int type
            df_product = get_data().astype({'code': str}).query('code == @code')

            # If failed, we search for in int
            if df_product.shape[0] == 0:
                code_int = int(code)
                df_product = get_data().query('code == @code_int')

            # And another solution it helps to deal with the 0 problem.
            if df_product.shape[0] == 0:
                print("Failed to load")
                code = "0"*(13 - len(code)) + code
                df_product = get_data().query('code == @code')

            # We get the product's name
            product_name = df_product['product_name'].values[0]

            # Principale image
            selected_product_img = df_product['image_1'].values[0]

            # Secondaries images
            # Return the link of the images
            
            others_img = [df_product[img].values[0] for img in [f"image_{i}" for i in range(1,5,1)]]

            # Display image if link correct
            others_img_style = [{'height': '150px', 'width': '150px'}
                               if "http" in str(others_img[i]) else no_display
                               for i in range(0, 4)]

            selected_product_title = html.Strong(product_name)
            selected_product_texte = get_texte_product(df_product.iloc[0], language)

            pnns1 = df_product["pnns_groups_1"].values[0]
            pnns2 = df_product["pnns_groups_2"].values[0]

            # We add to the navigation history
            history_nav.insert(0, [f"Product: {product_name}", country, pnns1, pnns2, None, code])

            # If the product visualize is the same as before, we prevent some of the front end update
            if pnns2 == prevent_update:

                title = dash.no_update
                subtitles = [dash.no_update] * len(diets)
                styles_images = [dash.no_update] * TOTAL_IMAGES
                textes_images = [dash.no_update] * TOTAL_IMAGES

                prevent_update, pnns1_chosen, pnns2_chosen = ([dash.no_update]*3)

            else:
                df = return_df(country, pnns1, pnns2).copy()

                title = html.Strong(translations[language]['best_recommended_products'])

                subtitles, images, styles_images, textes_images = generate_texte_image(df, diets, n_best, 
                                                                                       subtitles, images, 
                                                                                       styles_images, textes_images,
                                                                                       language)
                # Replace images by default if something failed in retrieving url
                images = [dash.get_asset_url('no_image.jpg') if url is np.nan else url for url in images]
                
                prevent_update = pnns2
                pnns1_chosen, pnns2_chosen = pnns1, pnns2
            
        except Exception as e:
            print(f"Error: {str(e)}")
        
            selected_product_img = dash.get_asset_url("no_image.jpg")
            selected_product_title = html.Strong(translations[language]['product_not_found'])
            selected_product_texte = html.Strong(translations[language]['product_not_available'])

            title = dash.no_update
            subtitles = [dash.no_update] * len(diets)
            styles_images = [dash.no_update] * TOTAL_IMAGES
            textes_images = [dash.no_update] * TOTAL_IMAGES
            prevent_update = None
        
        selected_product_style = {'display':'block'}
        style_top_graph_button = {'display':'block', 'color': 'black'}
        
    elif ctx.triggered_id == 'advanced_search_button':
        
        advanced_search_style = {'float': 'center', 'display': 'block', 'flex-direction': 'row', 
                                'width': '100%', 'background-color': '#F0F0F0', 'margin-bottom': '20px'}
        prevent_update = None
        
    # Top keep tract of the images src to load when clicking on 
    for i, src in enumerate(images):
        key = f'{diets[int(i/20)]}_img_{i%20}'
        if src == dash.no_update or src == None:
            continue
        else:
            shown_img_data[key] = src
            
    if condition_selected_a_product == False:
        pnns1_chosen = dash.no_update
        pnns2_chosen = dash.no_update
            
    output_values = [title, *subtitles, *images, *styles_images, *textes_images, *others_img, *others_img_style,
                     graphic_gestion_style_bottom, graphic_gestion_style_top, style_bottom_graph_button, style_top_graph_button, 
                     selected_diet, selected_product_style, 
                     selected_product_img, selected_product_title, selected_product_texte,
                     advanced_search_style, search_on, shown_img_data, history_nav, style_multiple_dropdown, 
                     browser_history_style, prevent_update, pnns1_chosen, pnns2_chosen, style_picture_search_div, data_figure]
    
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
    *[Output(f"graph_products_img_{pos}", 'figure') for pos in ['bottom', 'top']],
    *[Output(f"graphic_gestion_{pos}", 'style', allow_duplicate=True) for pos in ['bottom', 'top']],

    *[Input(f"{pos}_button_graphic", 'n_clicks') for pos in ['bottom', 'top']],
    *[Input(f"dropdown_nutrients_img_{pos}", 'value') for pos in ['bottom', 'top']],
    *[Input(f"check_list_graph_img_{pos}", 'value') for pos in ['bottom', 'top']],
    
    State('pnns1_chosen', 'data'),
    State('pnns2_chosen', 'data'),
    State('dropdown_country','value'),
    
    State('personnalized_sorting', 'data'),
    State('sliced_file', 'data'),
    State("dropdown_diet", "value"), 
    State('search_on', 'data'),
    State('dropdown_number_product', 'value'),
    State('language_user', 'data'),
    
    prevent_initial_call=True,
)
# When modifying the graphic
def modifying_graph(bottom_button, top_button, nutrients_choice_bottom, nutrients_choice_top, ch_list_graph_bottom, ch_list_graph_top,
                    pnns1_chosen, pnns2_chosen, country, selected_diet, df_slice, dropdown_diet, search_on, n_best, language):
    elapsed_time = time.time() if DEBUG else None

    # We do not update at first. Only the one selected will be updated
    figure_bottom, figure_top = dash.no_update, dash.no_update
    graphic_gestion_style_bottom, graphic_gestion_style_top = dash.no_update, dash.no_update
    
    # We use the patch for smaller modification
    patched_figure_bottom, patched_figure_top = Patch(), Patch()

    if search_on:
        df = pd.read_json(StringIO(df_slice), orient='split')         
        df_N_best = df_sorting(dropdown_diet, df).head(n_best)
    else:
        df = return_df(country, pnns1_chosen, pnns2_chosen)
        df_N_best = df_sorting(selected_diet, df).head(n_best)

    if ctx.triggered_id in ["bottom_button_graphic", "dropdown_nutrients_img_bottom", "check_list_graph_img_bottom"]:
        graphic_gestion_style_bottom = {'display':'block'}
        graphic_gestion_style_top = {'display':'None'}

        if ctx.triggered_id == "check_list_graph_img_bottom":
            figure_bottom = create_figure_products(df, nutrients, nutrients_choice_bottom, ch_list_graph_bottom, df_N_best, language)
            
        else:
            nutrients_choice = nutrients_choice_bottom if nutrients_choice_bottom not in [None, []] else nutrients
            figure_bottom = patch_graphic(patched_figure_bottom, df, df_N_best, ch_list_graph_bottom, nutrients_choice, ["A", "B"], language)

    elif ctx.triggered_id in ["top_button_graphic", "dropdown_nutrients_img_top", "check_list_graph_img_top"]:
        graphic_gestion_style_bottom = {'display':'None'}
        graphic_gestion_style_top = {'display':'block'}
        
        if ctx.triggered_id == "check_list_graph_img_bottom":
            figure_bottom = create_figure_products(df, nutrients, nutrients_choice_bottom, ch_list_graph_bottom, df_N_best, language)

        else:
            nutrients_choice = nutrients_choice_top if nutrients_choice_top not in [None, []] else nutrients
            figure_top = patch_graphic(patched_figure_top, df, df_N_best, ch_list_graph_top, nutrients_choice, ["A", "B"], language)
    
    print("modifying_graph: ", time.time() - elapsed_time) if DEBUG else None 
    
    return figure_bottom, figure_top, graphic_gestion_style_bottom, graphic_gestion_style_top

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
    Output('browser_history_div', 'style', allow_duplicate=True),
    Output('advanced_search_div', 'style', allow_duplicate=True),
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
        advanced_search_style = {'display':'None'}
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
            if type_search_product == "product_name":
                # We eliminate "product: " to conserve the name of the product
                search_bar = selected_history[0].lstrip('Product: ')
            elif type_search_product == "product_code":
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
            
    output_values = [style_images_gestion, style_browser_history, advanced_search_style,
                     df_history_nav, columns, selected_rows, country, pnns1, pnns2, 
                     loading_history, search_bar, *clicks_diet]
    
    print("browsing_history", time.time() - elapsed_time) if DEBUG else None  
    return tuple(output_values)

@app.callback(
    Output('dummy_output', 'children'),
    Input('picture_search_button','n_clicks'),
    Input('upload_img_button','n_clicks'),
    Input('clear_img_button','n_clicks'),
    Input('search_pnns1_img','n_clicks'),
    Input('search_pnns2_img','n_clicks'),
    Input('upload_img_data', 'contents'),
    Input('model_figure_result','clickData'),

    background=True,
    manager=background_callback_manager,
    
    prevent_initial_call=True,
)

# Will handle everything linked to the search by a picture
def wake_up_api(*args):
    # ping app to wake it up
    requests.head(api_classification_url)
    return None

@app.callback(
    Output('picture_search_div', 'style', allow_duplicate=True),
    Output('advanced_search_div', 'style', allow_duplicate=True),
    Output('browser_history_div', 'style', allow_duplicate=True),
    Output('images_gestion', 'style', allow_duplicate=True),
    Output('upload_img_button','style'),
    Output('clear_img_button','style'),
    Output('search_pnns1_img','style'),
    Output('search_pnns2_img','style'),
    Output('result_model_image','style'),
    Output('uploaded_img','children'),
    Output('model_figure_result','figure'),
    Output('pnns1_chosen', 'data', allow_duplicate=True),
    Output('pnns2_chosen', 'data', allow_duplicate=True),
    
    Input('picture_search_button','n_clicks'),
    Input('upload_img_button','n_clicks'),
    Input('clear_img_button','n_clicks'),
    Input('search_pnns1_img','n_clicks'),
    Input('search_pnns2_img','n_clicks'),
    Input('upload_img_data', 'contents'),
    Input('model_figure_result','clickData'),

    State('language_user', 'data'),
    background=True,
    manager=background_callback_manager,
    
    prevent_initial_call=True,
)
# Will handle everything linked to the search by a picture
def picture_search_div(*args):
    elapsed_time = time.time() if DEBUG else None

    display_no_show = {'display':'None'}
    
    # We display the div
    style_div = {'float': 'center', 'display': 'block', 'flex-direction': 'row', 'width': '100%'}
    style_others_div = [display_no_show]*3
                     
    image_contents = args[-3]
    clicked_graphic = args[-2]
    language = args[-1]
    
    uploaded_img_div = dash.no_update
    style_search_pnns1 = dash.no_update
    style_search_pnns2 = dash.no_update
    style_upload_button = dash.no_update
    style_clear_button = dash.no_update
    style_result_model = display_no_show
    figure = dash.no_update
    pnns1_chosen, pnns2_chosen = dash.no_update, dash.no_update 
    
    if ctx.triggered_id == "upload_img_button":
        uploaded_img_div = None
        image_contents = None
    
    elif ctx.triggered_id == "upload_img_data":
        style_upload_button = display_no_show
        style_clear_button = return_style16_nd()
        style_search_pnns1 = return_style16_nd()
        style_search_pnns2 = return_style16_nd()
        
        uploaded_img_div = html.Img(src=image_contents, style={'width': '500px', 'height':'500px'})
        
    elif ctx.triggered_id in ["clear_img_button", "picture_search_button"]:
        style_upload_button = return_style16_nd()
        style_clear_button = display_no_show
        style_search_pnns1 = display_no_show
        style_search_pnns2 = display_no_show
        uploaded_img_div = None
        image_contents = None
        
    elif ctx.triggered_id in ["search_pnns1_img", "search_pnns2_img"]:
        style_result_model = {'display': 'flex', 'flex-direction': 'column', 'width': '100%', 'margin-top':'20px',
                              'border-bottom': '1px solid black', 'border-top': '4px solid black'}
        
        # We send the image to the model
        if ctx.triggered_id == "search_pnns1_img":
            image_contents = {"base64_image": image_contents, "pnns_groups": "pnns_groups_1"}
        elif ctx.triggered_id == "search_pnns2_img":
            image_contents = {"base64_image": image_contents, "pnns_groups": "pnns_groups_2"}
        
        response = requests.post(api_classification_url + "pnns-process-image/", data=image_contents)
        
        try:
            # We put the result into a dataframe
            df_result = pd.DataFrame(response.json())

            # We show the result with a graphic
            # For now, only 3 results, could be expanded with a button
            figure = figure_result_model(df_result.iloc[:3], language)
        
        except:
            html.A("Format not compatible")
        
    elif ctx.triggered_id == "model_figure_result":
        
        # We hide the div
        style_div = display_no_show
        
        # We extract the chosen result by the user 
        pnns_chosen = clicked_graphic["points"][0]["y"]
        
        # We attribute the pnns1 and 2 associated
        if pnns_chosen in pnns_groups_1:
            pnns1_chosen = pnns_chosen
            pnns2_chosen = None
        elif pnns_chosen in pnns_groups_2:
            pnns1_chosen = next((key for key, value in pnns_groups.items() if pnns_chosen in value), None)
            pnns2_chosen = pnns_chosen
    
    output_values = [style_div, *style_others_div, style_upload_button, style_clear_button, style_search_pnns1, 
                     style_search_pnns2, style_result_model, uploaded_img_div, figure, pnns1_chosen, pnns2_chosen]
    
    print("picture_search_div", time.time() - elapsed_time) if DEBUG else None  

    return tuple(output_values) 

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
    