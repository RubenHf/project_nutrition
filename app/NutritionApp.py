import dash
from dash import Dash, html, dash_table, dcc, callback, Output, Input, State, ctx, Patch
from dash.dash_table.Format import Format, Scheme
import pandas as pd
import plotly
import plotly.express as px
import plotly.subplots as sp
from plotly.subplots import make_subplots
import copy
import os
import math
from io import StringIO
import time
import json

# Get the directory of the script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Go up one level to the parent directory (assuming the script is in the 'app' directory)
app_dir = os.path.dirname(script_dir)

# Define the path to the file in the /files directory
file_path = os.path.join(app_dir, 'files', 'cleaned_data.csv')

# Now you can use the file_path to access your file
with open(file_path, 'r') as file:
    data = pd.read_csv(file_path, sep = "\t")


def pnns_groups_options(df, country, pnns_groups_num, pnns1=None):
    if pnns_groups_num == "pnns_groups_1":
        pnns_groups = df[pnns_groups_num].unique()
    elif pnns_groups_num == "pnns_groups_2":
        pnns_groups = df.loc[df.pnns_groups_1 == pnns1, pnns_groups_num].unique()

    # Create a DataFrame with counts for each pnns group
    counts_df = data.query('countries_en.str.contains(@country)').groupby(pnns_groups_num).size().reset_index(name='count')

    # Merge the counts with the unique pnns groups
    merged_df = pd.DataFrame({pnns_groups_num: pnns_groups})
    merged_df = pd.merge(merged_df, counts_df, on=pnns_groups_num, how='left').fillna(0)
    
    merged_df.sort_values(by=pnns_groups_num, inplace=True)
    
    # Create the pnns_groups_options list
    pnns_groups_options = [
        {
            'label': f"{pnns} [{count} products]",
            'value': pnns
        }
        for pnns, count in zip(merged_df[pnns_groups_num], merged_df['count'])
    ]

    return pnns_groups_options

# Function to generate a RangeSlider
def generate_slider(title, id, max_value):
    return html.Div([title,
                     dcc.RangeSlider(0, max_value, 1, value=[0, max_value],
                                    marks={0: "0", max_value: str(max_value)},
                                    id=id,
                                    tooltip={"placement": "bottom", "always_visible": True})
                     ], style={'textAlign': 'center', 'color': 'black', 'fontSize': 15})


# Function to generate a DropDown
def generate_dropdown(value, options, placeholder, multi, id, clearable = True):
    return dcc.Dropdown(
                value=value,
                options=options,
                style={'fontFamily': 'monospace', 'align-items': 'center', 'justify-content': 'center', 'textAlign': 'center', 'color': 'black', 'fontSize': 15, 'width': '100%'},
                placeholder=placeholder,
                multi=multi,
                id=id,
                clearable=clearable,
            )

def empty_figure():
    """
    Function returning an empty figure with all the same template
    """
    fig = px.strip()
    # Set the background    
    fig.update_layout(
    plot_bgcolor='white'
    )
    fig.update_xaxes(
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='lightgrey'
    )
    fig.update_yaxes(
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='lightgrey'
    )
    fig.add_annotation(text="No data to show", x=0.5, y=0.5, showarrow=False,
                        font=dict(color="Black", size=20))
    return fig

def figure_radar_plot(df_slice, nutrients, nutrients_choice, df_selected_products):

    # We retrieve the mediane for the nutrients
    if len(nutrients_choice) == 0 :
        median_df = df_slice[nutrients].median()
    else:
        median_df = df_slice[nutrients_choice].median()
    
    # To put Energy and the nutrients on the same graph but with differents scales
    #figure = make_subplots(specs=[[{"secondary_y": True}]])

    # We repeat the first at the end to close the radarplot
    values = median_df.values.tolist() + [median_df.values[0]]
    columns = median_df.index.tolist() + [median_df.index[0]]
    
    #figure_energy = px.line_polar(r = values_energy, theta = columns, markers=True)
    figure_radar = px.line_polar(r = values, theta = columns, markers=True)

    # To fill the plot
    figure_radar.update_traces(fill='toself',
                               line_color = "green",
                               name=f"Median of {df_slice.shape[0]} products",
                               showlegend = True)
    
    # Update radial axis range
    #figure_radar.update_polars(radialaxis=dict(range=[0, 100]))
    
    nb_selected_product = 0
    
    # if product(s) have been selected
    if df_selected_products is not None:
        if not isinstance(df_selected_products, pd.DataFrame):
            # Assuming df_selected_products is a JSON-formatted string
            df_selected_products = pd.read_json(StringIO(df_selected_products), orient='split')

        if df_selected_products.shape[0] > 0 :
            nb_selected_product = df_selected_products.shape[0]

            # Differents blue colors
            blue_colors = [
                "#0077cc", "#00b8ff", 
                "#009688", "#35a79c", "#54b2a9", "#65c3ba", "#83d0c9",
                "#daf8e3", "#97ebdb", "#00c2c7", "#0086ad", "#005582",
                "#77aaff", "#99ccff", "#bbeeff", "#5588ff", "#3366ff",
            ]

            # We add a radarplot trace for each
            for i in range(df_selected_products.shape[0]):

                if len(nutrients_choice) == 0 :
                    mask = df_selected_products.iloc[i][nutrients]
                else:
                    mask = df_selected_products.iloc[i][nutrients_choice]

                # We get the values
                values = mask.values.tolist() + [mask.values[0]]
                columns = mask.index.tolist() + [mask.index[0]]

                # We create the new trace
                selected_radar_figure = px.line_polar(r = values, theta = columns, markers=True)

                selected_radar_figure.update_traces(fill='toself')
                selected_radar_figure.update_traces(fill='toself',
                                                    line_color = blue_colors[i],
                                                    showlegend = True)

                full_name = df_selected_products.iloc[i].product_name

                truncated_name = full_name[:20]
                selected_radar_figure.update_traces(name = truncated_name,
                                          legendgroup = full_name)#,
    #                                      hovertemplate = full_name)

                # We add it to the main figure_radar
                figure_radar.add_trace(selected_radar_figure.data[0])

    # To change the order and put the Median on top
    figure_radar.data = figure_radar.data[::-1]
    figure_radar.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        font=dict(color="black"),
    )
    
    taille = 1 if nb_selected_product < 3 else nb_selected_product/4
    
    figure_radar.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.1*taille, xanchor="left", x=0.2,
                                          font=dict(size=10),itemwidth=30))
    # We change the hovertemplate names
    figure_radar.update_traces(
        hovertemplate='<br>%{theta} = %{r}' # nutrient = value
        )
        # Set the background  
    figure_radar.update_polars(bgcolor='white')
    figure_radar.update_layout(
        font_size = 15,
        polar = dict(
          bgcolor = "rgb(223, 223, 223)",
          angularaxis = dict(
            linewidth = 3,
            showline=True,
            linecolor='black'
          ),
          radialaxis = dict(
            side = "counterclockwise",
            showline = True,
            linewidth = 2,
            gridcolor = "white",
            gridwidth = 2,
          )
        ),
    )
    
    return figure_radar
        
        
        
def create_figure_products(df, list_nutrients, selected_nutrients, selected_graphical_type, df_selected_products):
    """
        V2 of the function creating the different graphics used in the dashboard
        Transitioning from a boxplot to a violinplot
        Each figures will have the full page
        Less conflicts, better integration in the dashboard.
        
        df: dataframe containing the data to project
        list_nutrients: columns projected (nutrients) 
        selected_nutrients: selected columns from the list_nutrients
        selected_graphical_type: type of graphic that will be projected
        selected_products: selected products that will be highlighted
    """
    
    # To put Energy and the nutrients on the same graph but with differents scales
    figure = make_subplots(specs=[[{"secondary_y": True}]])
    
    selected_nutrients = [] if selected_nutrients == None else selected_nutrients

    if selected_graphical_type in ["Distribution", "Products"]:
        if selected_graphical_type == "Distribution": 
            figure_energy = px.violin(df, y="energy_100g", box=False) 
            figure_others = (px.violin(df, y=selected_nutrients, box=False) 
                             if len(selected_nutrients) > 0 
                             else px.violin(df, y=list_nutrients, box=False))

            figure_others.update_traces(width = 1)

        elif selected_graphical_type == "Products":
            figure_energy = px.strip(df, y="energy_100g") 
            figure_others = (px.strip(df, y=selected_nutrients) 
                                 if len(selected_nutrients) > 0 
                                 else px.strip(df, y=list_nutrients))  
            
        figure_energy['data'][0]['customdata'] = [name for name in df['product_name']]
        if len(selected_nutrients) > 0 :
            figure_others['data'][0]['customdata'] = [name for name in df['product_name']] * len(selected_nutrients)
        else:
            figure_others['data'][0]['customdata'] = [name for name in df['product_name']] * len(nutrients)
        
        figure_energy.update_traces(marker = dict(color = "red"), hovertemplate='<br>Product name: %{customdata}<br>energy_100g = %{y}')
        figure_others.update_traces(marker = dict(color = "green"), hovertemplate='<br>Product name: %{customdata}<br>%{x}: %{y}')
                
                         
        if df_selected_products is not None:
            if not isinstance(df_selected_products, pd.DataFrame):
                # Assuming df_selected_products is a JSON-formatted string
                df_selected_products = pd.read_json(StringIO(df_selected_products), orient='split')

            figure_energy_selected = px.strip(df_selected_products, y="energy_100g") 
            figure_others_selected = (px.strip(df_selected_products, y=selected_nutrients) 
                                 if len(selected_nutrients) > 0 
                                 else px.strip(df_selected_products, y=list_nutrients))
            # Putting informations
            figure_energy_selected['data'][0]['customdata'] = [name for name in df_selected_products['product_name']]
            if len(selected_nutrients) > 0:
                figure_others_selected['data'][0]['customdata'] = [name for name in df_selected_products['product_name']] * len(selected_nutrients)
            else:
                figure_others_selected['data'][0]['customdata'] = [name for name in df_selected_products['product_name']] * len(nutrients)
            figure_energy_selected.update_traces(hovertemplate='<br>Product name: %{customdata}<br>energy_100g = %{y}')
            figure_others_selected.update_traces(hovertemplate='<br>Product name: %{customdata}<br>%{x}: %{y}')

        else :
            figure_energy_selected = px.strip()
            figure_others_selected = px.strip()
            
        for fig in [figure_energy_selected, figure_others_selected]:   
            fig.update_traces(marker = dict(color = "blue"), 
                                marker_size=8, name="Selected", 
                                marker_line_color="black", marker_line_width=2)
                         
        for i in range(len(figure_energy.data)):
            figure.add_trace(figure_energy.data[i], secondary_y=False)
            figure.add_trace(figure_others.data[i], secondary_y=True)
            figure.add_trace(figure_energy_selected.data[i], secondary_y=False)
            figure.add_trace(figure_others_selected.data[i], secondary_y=True)

            #
           # if isinstance(df_selected_products, pd.DataFrame): 
            #    figure.add_trace(figure_energy_selected.data[i], secondary_y=False)
             #   figure.add_trace(figure_others_selected.data[i], secondary_y=True)

        # Update of figure layout
        figure.update_layout(
            yaxis_title="g/100g",
            title=dict(text=f'Distribution of macronutrients of selected products [{df.shape[0]}]',
                       font=dict(size=24, color="black"), x=0.5, xanchor='center'),
            font=dict(size=18, color="black"),
            plot_bgcolor='white',
        )

        # Set y-axes titles and background
        figure.update_yaxes(
            title_text="g/100g (energy)", 
            secondary_y=False,
            mirror=True,
            ticks='outside',
            showline=True,
            linecolor='black',
            gridcolor='lightgrey')
                             
        figure.update_yaxes(
            title_text="g/100g (nutrients)", 
            secondary_y=True) 
                             
        # Set x-axe ticks
        figure.update_xaxes(
            ticktext=["energy_100g"] + nutrients, 
            tickvals=[i for i in range(len(nutrients) + 1)],
            mirror=True,
            ticks='outside',
            showline=True,
            linecolor='black',
            gridcolor='lightgrey')
            #range = [0, 100], tickmode="sync")
        return figure
                
    elif selected_graphical_type == "Radarplot":
        return figure_radar_plot(df, list_nutrients, selected_nutrients, df_selected_products)
    
    # Default, but shouldn't occur
    else:
        return empty_figure()
    

def cache(fun):
    cache.cache_ = {}

    def inner(country, pnns1, pnns2):
        # Check if the inputs have changed
        inputs_changed = (
            country not in cache.cache_ or
            pnns1 not in cache.cache_ or
            pnns2 not in cache.cache_
        )
        
        cache_key = (country, pnns1, pnns2)

        if inputs_changed or cache_key not in cache.cache_:
            cache.cache_[cache_key] = fun(country, pnns1, pnns2)

        return cache.cache_[cache_key]

    return inner

@cache
def function(country, pnns1, pnns2):
    df = data.query('countries_en.str.contains(@country)')

    if pnns1:
        df = df[df.pnns_groups_1 == pnns1]
    if pnns2:
        df = df[df.pnns_groups_2 == pnns2]

    return df

def return_df(country, pnns1 = None, pnns2 = None):

    if country:
        return function(country, pnns1, pnns2)

    # Returning no data to show
    else:
        return None

def get_image(code):
    # Transform the code to produce the Open Food Facts image URL
    if len(code) <= 8:
        url = f'https://images.openfoodfacts.org/images/products/{code}/1.jpg'
        return url
    elif len(code) > 8:
        code = "0"*(13 - len(code)) + code
        url = f'https://images.openfoodfacts.org/images/products/{code[:3]}/{code[3:6]}/{code[6:9]}/{code[9:]}/1.jpg'
        return url
    else:
        return None
        
def get_code(url):
    # Extract the product code from the Open Food Facts image URL
    try:
        parts = url.split('/')
        
        # Short code format
        if parts[-3] == 'products':
            return parts[-2]
        
        # Long code format
        else:
            code = parts[-5] + parts[-4] + parts[-3] + parts[-2]
            return code.lstrip('0')  # Remove leading zeros
    except:
        pass

    return None

def mapping_nutriscore_IMG(df):
    """
        Function matching the nutriscore to the letter A to E
        Add the column nutriscore_score_letter to the dataframe
        We loop inside the dictionnary, and change the letter if the score is inferior.
        Until it isn't
    """
    nutriscore_img = {
        "E" : ["40", "nutriscore_E.png"], 
        "D" : ["18", "nutriscore_D.png"],
        "C" : ["10", "nutriscore_C.png"],
        "B" : ["2", "nutriscore_B.png"],
        "A" : ["-1", "nutriscore_A.png"],
    }
    if isinstance(df, pd.DataFrame):   
        df["nutriscore_score_letter"] = "nutriscore_E.png"
        for letter in nutriscore_img:
            df.loc[: ,"nutriscore_score_letter"] = df.apply(lambda x: nutriscore_img[letter][1] 
                                                if x["nutriscore_score"] <= int(nutriscore_img[letter][0])
                                               else x["nutriscore_score_letter"], axis = 1)
        return df

def df_sorting(diet, df = None):
    """
        Function sorting the dataframe
        ascending = True
        Descending = False
    """

    type_diet = {
        "Healthier foods": [
            {'column_id': 'nutriscore_score', 'direction': True},
            {'column_id': 'fiber_100g', 'direction': False}
        ],
        "Low sugar foods": [
            {'column_id': 'carbohydrates_100g', 'direction': True},
            {'column_id': 'nutriscore_score', 'direction': True}
        ],
        "Protein rich foods": [
            {'column_id': 'proteins_100g', 'direction': False},
            {'column_id': 'nutriscore_score', 'direction': True}
        ],
        "Energy rich foods": [
            {'column_id': 'energy_100g', 'direction': False},
            {'column_id': 'nutriscore_score', 'direction': True}
        ],
        "Low fat foods": [
            {'column_id': 'fat_100g', 'direction': True},
            {'column_id': 'nutriscore_score', 'direction': True}
        ],
    }
    column_id = []
    direction = []
    
    df_copy = copy.deepcopy(df)
    
    if diet in type_diet:
        for sorting_param in type_diet[diet]:
            
            column_id.append(sorting_param['column_id'])
            direction.append(sorting_param['direction'])
            
        if isinstance(df, pd.DataFrame):  
            df_copy = df_copy.sort_values(by=column_id, ascending=direction)
    
    if isinstance(df_copy, pd.DataFrame):
        return df_copy
    else: 
        return column_id



##### Initialize the app - incorporate css
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)

server = app.server

app.title = 'Nutrition app'

versionning = "version: 0.6.2"

DEBUG = False

products_availability = "Referenced products: " + str(data.shape[0])

nutrients = ["fat_100g", "saturated-fat_100g", "carbohydrates_100g", "fiber_100g", "proteins_100g", "salt_100g", "macronutrients_100g"]

slider_trigger = ["slider_energy", "slider_fat", "slider_saturated", "slider_carbohydrates", "slider_fiber", "slider_proteins", "slider_salt", "slider_macronutrients"]

diets = ["Healthier foods", "Low sugar foods", "Protein rich foods", "Energy rich foods", "Low fat foods"]

# Default setup
default_country, default_pnns1, default_pnns2, default_diet = "France", "Fruits and vegetables", "Soups", "Healthier foods" 
default_graphic_option = "Distribution"

# Options setup for dropdown of countries
c1 = [country.split(",") for country in data.countries_en.unique()]
c2 = [count for country in c1 for count in country]
unique_countries = sorted(list(set(c2)))

flags = {"United States": "🇺🇸", "France":"🇫🇷", "Germany":"🇩🇪", "United Kingdom":"🇬🇧"}

# Generate list of unique countries
unique_countries = [
    {
        'label': f"{flags[country]} {country} [{return_df(country).shape[0]} products]",
        'value': country
    } 
    for country in unique_countries
]

# Generate columns with appropriate formatting for numeric columns for dash DataTable
columns = [
    {
        'name': col,
        'id': col,
        'type': 'numeric' if pd.api.types.is_numeric_dtype(data[col]) else 'text',
        'format': Format(precision=2, scheme=Scheme.fixed) if (pd.api.types.is_numeric_dtype(data[col]) and col in nutrients) else Format(precision=0, scheme=Scheme.fixed)
    }
    for col in data.columns
    if col not in ["countries_en", "pnns_groups_1", "pnns_groups_2"]
]

# Generate pnns_groups 1 and 2, and sorted
pnns_groups_1 = sorted(data.pnns_groups_1.unique())

pnns_groups_2 = []
for pnns1 in sorted(data.pnns_groups_1.unique()):
    for pnns2 in sorted(data.loc[data.pnns_groups_1 == pnns1, 'pnns_groups_2'].unique()):
        if pnns2 not in ['unknown', 'Alcoholic beverages']:
            pnns_groups_2.append(pnns2)

pnns_groups = {}
for pnns1 in pnns_groups_1:
    pnns_groups[pnns1] = sorted(data.loc[data.pnns_groups_1 == pnns1, "pnns_groups_2"].unique().tolist())

app.layout = html.Div([
    # Left side
    html.Div([    
        # Image of the dashboard
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
            for pnns1 in pnns_groups_options(data, default_country, "pnns_groups_1")
            for y, pnns2 in enumerate(pnns_groups_options(data, default_country, "pnns_groups_2", pnns1["value"]))
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
            style={'font-size': '20px', 'color': 'black',  
                   'textAlign': 'center', 'border': '1px solid black'}
        ),
        
        # Informations
        html.Div([
            html.Div(className='row', children="Ruben HALIFA"),

            html.Div(className='row', children=versionning),

            html.Div(className='row', children=products_availability),
        ], style={'textAlign': 'left', 'color': 'black', 'fontSize': 12}),
    ], style={'background-color': '#F0F0F0', 'overflowY': 'scroll', 'height': '100vh', 'flex': '1', 'direction': 'rtl'}),
    
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
                                html.Img(id=f"{diet}_img_{i}", src=dash.get_asset_url('no_image.jpg'), n_clicks = 0,
                                         alt="No image available", style={'height': '200px', 'width': '200px'}),
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
    
], style={'display': 'flex', 'justify-content': 'space-between', 'margin': '0', 'padding': '0'})


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
        
        pnns_groups_1_options = pnns_groups_options(data, country, "pnns_groups_1")
        
        for pnns1 in pnns_groups_1_options:
            output_values.append(pnns1["label"])

        for pnns1 in pnns_groups_1_options:
            for pnns2 in pnns_groups_options(data, country, "pnns_groups_2", pnns1["value"]):
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
    
    # If clicking on diet preference
    if ctx.triggered_id in [f'{diet}_div' for diet in diets] + ['search_confirmation_button']:
              
        for i, diet in enumerate([diet + "_div" for diet in diets]):
            if ctx.triggered_id == 'search_confirmation_button':
                if diet[:-4] == dropdown_diet:
                    selected_diet = diets[i] # To keep the selected button
                    advanced_search_style = dash.no_update
                    df = pd.read_json(StringIO(df_slice), orient='split')
                    search_on = True
                    
            else:
                # Add information when it is the selected diet
                if diet == ctx.triggered_id:
                    search_on = False
                    selected_diet = diets[i] # To keep the selected button
                    advanced_search_style = {'display':'None'}
                    # sort and retrieve the N best, then match the nutriscore image           
                    df_N_best = df_sorting(diets[i], df).head(n_best)
                    df_N_best = mapping_nutriscore_IMG(df_N_best)

                    title = html.Strong(f"BEST RECOMMENDED PRODUCTS FOR {diets[i].upper()}")
                    subtitles.append(html.Strong(f"{diets[i]}"))

                    for _, row in df_N_best.iterrows():

                        images.append(get_image(str(row.iloc[0])))
                        styles_images.append({'width': '350px', 'height': '350px'})

                        textes_images.append(
                            html.Div([
                                html.Div([
                                    html.Strong(f"{col}:"),
                                    f" {row[col]}"],
                                    style={'text-align': 'left', 'margin-top': '1px', 'margin-left':'10px'}
                                )
                                for col in row.index[:-1]  # Exclude the last column (nutriscore_image)
                            ] + [
                                html.Img(
                                src=dash.get_asset_url(str(row.iloc[-1])),
                                    alt="Product Nutriscore",
                                    style={'width': '100px', 'height': '50px', 'margin-left':'10px'}
                                ),
                            ], style={'display': 'flex', 'flex-direction': 'column', 'width': '100%'}))
                    # We complete
                    if df_N_best.shape[0] < 20:
                        images = images + [None] * (20 - df_N_best.shape[0])
                        styles_images = styles_images + [{'display':'None'}] * (20 - df_N_best.shape[0])
                        textes_images = textes_images + [None] * (20 - df_N_best.shape[0])
                        
                
                # Add blanks when it is not the selected one
                else:
                    
                    subtitles.append(html.Strong(f"{diets[i]}"))  
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
                    html.Div(product_name, style={'text-align': 'center', 'margin-top': '5px'}) 
                    ] + [
                        html.Img(
                        src=dash.get_asset_url(str(IMG.iloc[-1])),
                            alt="Product Nutriscore",
                            style={'width': '100px', 'height': '50px', 'margin-left':'10px'}
                        ),
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
        if ctx.triggered_id == ["search_bar"]:
            df_product = data.query('product_name == @search_bar')
            
        else: 
            #shown_img_data[ctx.triggered_id]
            url = shown_img_data[ctx.triggered_id]
            code = get_code(url)
            df_product = data.query('code == @code')
            
        # We search for the product [Only one for now]
        df_product = df_product.head(1) if df_product.shape[0] > 1 else df_product
        df_product = mapping_nutriscore_IMG(df_product)
        
        selected_product_img = get_image(str(df_product["code"].values[0]))
        selected_product_title = html.Strong(f"{df_product['product_name'].values[0]}")
        selected_product_texte = html.Div([
            html.Div([
                html.Strong(f"{col}:"),
                f" {df_product[col].values[0]}"],
                style={'text-align': 'left', 'margin-top': '1px', 'margin-left':'10px'}
            )
            for col in df_product.columns[:-1]  # Exclude the last column (nutriscore_image)
            ] + [
                html.Img(
                src=dash.get_asset_url(str(df_product["nutriscore_score_letter"].values[0])),
                    alt="Product Nutriscore",
                    style={'width': '100px', 'height': '50px', 'margin-left':'10px'}
                ),
            ], style={'display': 'flex', 'flex-direction': 'column', 'width': '100%'})
                   
        pnns1 = df_product["pnns_groups_1"].values[0]
        pnns2 = df_product["pnns_groups_2"].values[0]
        
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
                    html.Div(product_name, style={'text-align': 'center', 'margin-top': '5px'}) 
                    ] + [
                        html.Img(
                        src=dash.get_asset_url(str(IMG.iloc[-1])),
                            alt="Product Nutriscore",
                            style={'width': '100px', 'height': '50px', 'margin-left':'10px'}
                        ),
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

# Run the app
if __name__ == '__main__':
    app.run(debug=False)
    