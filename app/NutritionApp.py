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


def pnns_groups_options(df, country, pnns_groups_num, pnns1 = None):
    if pnns_groups_num == "pnns_groups_1":
        pnns_groups = df[pnns_groups_num].unique()
    elif pnns_groups_num == "pnns_groups_2":
        pnns_groups = df.loc[df.pnns_groups_1 == pnns1, pnns_groups_num].unique()

    pnns_groups = [
    {
        'label': f"{pnns} [{df[df.countries_en.str.contains(country)&(df[pnns_groups_num] == pnns)].shape[0]} products]",
        'value': pnns
    } 
    for pnns in pnns_groups
    ]

    return pnns_groups

# Function to generate a RangeSlider
def generate_slider(title, id, max_value):
    return html.Div([title,
                     dcc.RangeSlider(0, max_value, 1, value=[0, max_value],
                                    marks={0: "0", max_value: str(max_value)},
                                    id=id,
                                    tooltip={"placement": "bottom", "always_visible": True})
                     ], style={'textAlign': 'center', 'color': 'black', 'fontSize': 15})


# Function to generate a DropDown
def generate_dropdown(value, options, placeholder, multi, id):
    return dcc.Dropdown(
                value=value,
                options=options,
                style={'textAlign': 'left', 'color': 'black', 'fontSize': 15, 'width': '100%'},
                placeholder=placeholder,
                multi=multi,
                id=id
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
    if (df_selected_products != None):
        df_selected_products = pd.read_json(StringIO(df_selected_products), orient='split')
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
        hovertemplate='<br>Value: %{r}<br>Nutrient: %{theta}'
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
            figure_energy = px.violin(df, y="energy_100g", hover_data=["product_name"], box=False) 
            figure_others = (px.violin(df, y=selected_nutrients, hover_data=["product_name"], box=False) 
                             if len(selected_nutrients) > 0 
                             else px.violin(df, y=list_nutrients, hover_data=["product_name"], box=False))

            figure_others.update_traces(width = 1)

        elif selected_graphical_type == "Products":
            figure_energy = px.strip(df, y="energy_100g", hover_data=["product_name"]) 
            figure_others = (px.strip(df, y=selected_nutrients, hover_data=["product_name"]) 
                                 if len(selected_nutrients) > 0 
                                 else px.strip(df, y=list_nutrients, hover_data=["product_name"]))  

        figure_energy.update_traces(marker = dict(color = "red"))
        figure_others.update_traces(marker = dict(color = "green"))
                
                         
        if df_selected_products != None:
            # We get the selected producted
            df_selected_products = pd.read_json(StringIO(df_selected_products), orient='split')

            figure_energy_selected = px.strip(df_selected_products, y="energy_100g", hover_data=["product_name"]) 
            figure_others_selected = (px.strip(df_selected_products, y=selected_nutrients, hover_data=["product_name"]) 
                                 if len(selected_nutrients) > 0 
                                 else px.strip(df_selected_products, y=list_nutrients, hover_data=["product_name"]))
                             
            for fig in [figure_energy_selected, figure_others_selected]:   
                fig.update_traces(marker = dict(color = "blue"), 
                                            marker_size=8, name="Selected", 
                                            marker_line_color="black", marker_line_width=2)
                         
        for i in range(len(figure_energy.data)):
            figure.add_trace(figure_energy.data[i], secondary_y=False)
            figure.add_trace(figure_others.data[i], secondary_y=True)
            #
            if isinstance(df_selected_products, pd.DataFrame): 
                figure.add_trace(figure_energy_selected.data[i], secondary_y=False)
                figure.add_trace(figure_others_selected.data[i], secondary_y=True)

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
    
    
def sorting_df(df, sort_by):
    """
        To sort the dataframe
    """
    if len(sort_by) :
        df.sort_values(
            [col['column_id'] for col in sort_by],
                ascending=[
                    col['direction'] == 'asc'
                        for col in sort_by
            ], inplace=True)

    return df

def row_coloring(dash_table, selected_row_ids, style_data_conditional):
    """
        To color the rows
    """
    for row_id in selected_row_ids:
        style_data_conditional.append({
            'if': {'row_index': row_id},
            'backgroundColor': "tomato" if row_id >= (len(dash_table) / 2) else "green",
            'color': 'white'
        })
    return style_data_conditional

def col_coloring(sort_by, style_data_conditional):
    """
        To color the columns
    """
    if len(sort_by) > 0:    
        for col in sort_by:
            # insert instead of append, to place them under the row coloring
            style_data_conditional.insert(0, {
                'if': {'column_id': col['column_id']},
                'backgroundColor': "#7cc6cb",
                'color': 'black'
            })  
    return style_data_conditional

##### Initialize the app - incorporate css
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)

server = app.server

app.title = 'Nutrition app'

versionning = "version: 0.5.0"

products_availability = "Referenced products: " + str(data.shape[0])

nutrients = ["fat_100g", "saturated-fat_100g", "carbohydrates_100g", "fiber_100g", "proteins_100g", "salt_100g", "macronutrients_100g"]

slider_trigger = ["slider_energy", "slider_fat", "slider_saturated", "slider_carbohydrates", "slider_fiber", "slider_proteins", "slider_salt", "slider_macronutrients"]

diets = ["Healthier foods", "Low sugar foods", "Protein rich foods", "Energy rich foods", "Low fat foods"]

# Default setup
default_country, default_pnns1, default_pnns2, default_diet = "France", "Fruits and vegetables", "Soups", "Healthier foods" 

# Options setup for dropdown of countries
c1 = [country.split(",") for country in data.countries_en.unique()]
c2 = [count for country in c1 for count in country]
unique_countries = sorted(list(set(c2)))

# Generate list of unique countries
unique_countries = [
    {
        'label': f"{country} [{data[data.countries_en.str.contains(country)].shape[0]} products]",
        'value': country
    } 
    for country in unique_countries
]

# Generate columns with appropriate formatting for numeric columns for dash DataTable
columns = [
            {'name': col, 'id': col, 'type': 'numeric', 'format': Format(precision=2, scheme=Scheme.fixed)}
            if col in nutrients
            else {'name': col, 'id': col, 'type': 'numeric', 'format': Format(precision=0, scheme=Scheme.fixed)}
        if pd.api.types.is_numeric_dtype(data[col])
        else {'name': col, 'id': col, 'type': 'text'}
    for col in data.columns
]

app.layout = html.Div([
    
    # Informations
    html.Div([
        html.Div(className='row', children="Ruben HALIFA"),
    
        html.Div(className='row', children=versionning),
        
        html.Div(className='row', children=products_availability),
    ], style={'textAlign': 'left', 'color': 'black', 'fontSize': 12}),
    
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
        generate_dropdown(default_country, unique_countries, "Choose a country", False, 'dropdown_country')
    ], style={'width': '33%', 'margin': '0 auto'}),
    
    # Dropdown for the pnns_groups_1
    html.Div([
        generate_dropdown(default_pnns1, [], "Choose a PNNS group 1", False, 'dropdown_pnns1')
    ], style={'display': 'inline-block', 'width': '50%', 'margin': '0 auto'}),
    
    # Dropdown for the pnns_groups_2
    html.Div([
        generate_dropdown(default_pnns2, [], "Choose a PNNS group 2", False, 'dropdown_pnns2')
    ], style={'display': 'inline-block', 'width': '50%', 'margin': '0 auto'}),
    
    # Dropdown for the diet
    html.Div([
        generate_dropdown(default_diet, diets, "Choose a nutrious plan", False, 'dropdown_diet')
    ], style={'width': '50%', 'margin': '0 auto'}),
        
    # Searchbar products
    html.Div([
        generate_dropdown(None, [], "Search a product", True, 'search_bar')
    ], style={'margin': '0 auto'}),
    
    # Dropdown for the macronutrient
    html.Div([
        generate_dropdown(None, nutrients, "Choose nutrients", True, 'dropdown_nutrients')
    ], style={'margin': '0 auto'}),
    
    
    # Checklist type of graph
    html.Div([
        dcc.RadioItems(
            value="Distribution",
            options=[
                        {'label': 'Radarplot', 'value': 'Radarplot'},
                        {'label': 'Distribution', 'value': 'Distribution'},
                        {'label': 'Products', 'value': 'Products'}
                    ],
            style={'textAlign': 'center', 'color': 'black', 'fontSize': 15, 'width': '100%'},
            inline=True,
            id='check_list_graph')
    ], style={'margin': 'auto'}),
    
    html.Div([
        html.Div([
        # Graph showing the distribution of the nutrients compare to the product
            dcc.Graph(id="graph_macronutrients", 
                      style={'height': '600px', 'width': '100%', 'float': 'left'}),
        ], style={'display': 'flex', 'flex-direction': 'row', 'width': '100%'}),

        # Sliders controling which products we show
        html.Div([
            # Button to reset sliders
            html.Div([
                html.Button(html.Strong("Reset"), id="reset_sliders_button", n_clicks=0, style={'color': 'black'})
                     ], style={'textAlign': 'center', 'color': 'black', 'fontSize': 15}),

                generate_slider("Energy kcal/100g", 'slider_energy', 3880),
                generate_slider("Fat g/100g", 'slider_fat', 100),
                generate_slider("Saturated_fat g/100g", 'slider_saturated', 100),
                generate_slider("Carbohydrates g/100g", 'slider_carbohydrates', 100),
                generate_slider("Fiber g/100g", 'slider_fiber', 100),
                generate_slider("Proteins g/100g", 'slider_proteins', 100),
                generate_slider("Salt g/100g", 'slider_salt', 100),
                generate_slider("Macronutrients g/100g", 'slider_macronutrients', 100)

            ], style={'width': '20%'}),
        ], style={'display': 'flex', 'flex-direction': 'row', 'width': '100%'}),
    
    # Table with data selection
    html.Div([
        html.Div(className='row', children="List of products by your search (max 20)",
             style={'textAlign': 'center', 'color': 'black', 'fontSize': 30}),
        html.Div( 
            dash_table.DataTable(
                data=None,
                columns=columns,
                page_size = 50,
                sort_action='native',
                sort_mode='multi',
                style_table={'overflowX': 'auto'},
                row_selectable='multi',
                selected_rows=[],
                style_cell={
                    'textAlign': 'center',
                    'height': 'auto',
                    'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
                    'whiteSpace': 'normal'
                },
                sort_by=[{'column_id':'nutriscore_score', 'direction':'asc'}], 
                id = "table_products"))
    ], style={'width': '100%'}),
    
    dcc.Store(id='initial_file', data=None),
    dcc.Store(id='intermed_file', data=None),
    dcc.Store(id='intermed_slide_file', data=None),
    dcc.Store(id='sliced_file', data=None),
    dcc.Store(id='personnalized_sorting', data=[]),
    dcc.Store(id='selected_product_table', data=None),
    dcc.Store(id='dropdown_search_bar_number', data=0),
    dcc.Store(id='dropdown_table_number', data=0),
    
    
])

@app.callback(
    Output('initial_file', 'data'),
    Output('intermed_file', 'data'),
    Output('intermed_slide_file', 'data'),
    Output('sliced_file', 'data'),
    
    Input('dropdown_country','value'),
    Input('dropdown_pnns1','value'),
    Input('dropdown_pnns2','value'),
    
    *[Input(f'{slide}', 'value') for slide in slider_trigger],
    
    State('initial_file', 'data'),
    State('intermed_file', 'data'),
    State('intermed_slide_file', 'data'),
    State('sliced_file', 'data'),
)

def data_slicing(country, pnns1, pnns2,
                 slide_energy, slide_fat, slide_sat_fat, slide_carbs, 
                 slide_fiber, slide_prot, slide_salt, slide_macro,
                 df_origin, df_intermediaire, df_inter_slide, df_slice):

    sliders = [slide_energy, slide_fat, slide_sat_fat, slide_carbs, slide_fiber, slide_prot, slide_salt, slide_macro]
    # Initial call
    if df_origin is None:
        df_origin = data.to_json(orient='split')
    
    # We do soething only if a country has been selected
    if country == None :
    
        return dash.no_update, None, None, None

    else :
        # Filtering based on country
        if ctx.triggered_id == "dropdown_country" or ctx.triggered_id is None:
            df_intermediaire = pd.read_json(StringIO(df_origin), orient='split')
            df_intermediaire = df_intermediaire[df_intermediaire.countries_en.str.contains(country)]

            df_inter_slide = copy.copy(df_intermediaire)
            
            # Verification of pnns conformity
            if pnns1 != None :
                df_inter_slide = df_inter_slide[df_inter_slide.pnns_groups_1 == pnns1]
            if pnns2 != None : 
                df_inter_slide = df_inter_slide[df_inter_slide.pnns_groups_2 == pnns2]

            df_slice = copy.copy(df_inter_slide)

            df_intermediaire = df_intermediaire.to_json(orient='split')
            df_inter_slide = df_inter_slide.to_json(orient='split')

            
        # Filtering based on pnns1
        if ctx.triggered_id in ["dropdown_pnns1"]:
            df_inter_slide = pd.read_json(StringIO(df_intermediaire), orient='split')
            # Verification of pnns conformity
            if pnns1 != None:
                df_inter_slide = df_inter_slide[df_inter_slide.pnns_groups_1 == pnns1]
                
            df_intermediaire, df_origin = dash.no_update, dash.no_update
            df_slice = copy.copy(df_inter_slide)
            df_inter_slide = df_inter_slide.to_json(orient='split')

        # Filtering based on pnns2
        if ctx.triggered_id in ["dropdown_pnns2"]:
            df_inter_slide = pd.read_json(StringIO(df_intermediaire), orient='split')
            # Verification of pnns conformity
            if (pnns1 != None) & (pnns2 != None):
                df_inter_slide = df_inter_slide[(df_inter_slide.pnns_groups_1 == pnns1) &
                                                (df_inter_slide.pnns_groups_2 == pnns2)]
            else :
                df_inter_slide = df_inter_slide[(df_inter_slide.pnns_groups_1 == pnns1)]
                
            df_intermediaire, df_origin = dash.no_update, dash.no_update
            df_slice = copy.copy(df_inter_slide)
            df_inter_slide = df_inter_slide.to_json(orient='split')

        # Filtering based on slide
        if ctx.triggered_id in slider_trigger:

            df_slice = pd.read_json(StringIO(df_inter_slide), orient='split')
            
            df_intermediaire, df_origin, df_inter_slide = dash.no_update, dash.no_update, dash.no_update

        for nutrient, slide in zip(["energy_100g"] + nutrients, sliders):
            if ctx.triggered_id not in slider_trigger:
                nutrient_min = math.floor(df_slice[f'{nutrient}'].min())
                nutrient_max = math.ceil(df_slice[f'{nutrient}'].max())
                df_slice = df_slice[(df_slice[nutrient] >= nutrient_min) & (df_slice[nutrient] <= nutrient_max)]
            elif ctx.triggered_id in slider_trigger:
                df_slice = df_slice[(df_slice[nutrient] >= slide[0]) & (df_slice[nutrient] <= slide[1])]

        df_slice = df_slice.to_json(orient='split') 
    return df_origin, df_intermediaire, df_inter_slide, df_slice


@app.callback(
    Output('dropdown_country','value'),
    
    Input('dropdown_country','value'),
)

# We define the countries list
def choice_country(country):
    
    if country == []:
        country = None
        
    return country
    
@app.callback(
    Output('dropdown_pnns1','options'),
    Output('dropdown_pnns2','options'),
    Output('dropdown_pnns1','value'),
    Output('dropdown_pnns2','value'),
    
    Input('dropdown_pnns1','value'),
    Input('dropdown_pnns2','value'),
    Input('dropdown_country','value'),
    
    State('dropdown_pnns1','options'),
    State('dropdown_pnns2','options'),
)

# We define the pnns_groups
def choice_pnns_groups(pnns1, pnns2, country, pnns_groups_1, pnns_groups_2):
    # Modifying only if necessary
    if ctx.triggered_id == "dropdown_country":
        if country is None:
            
            pnns_groups_1, pnns_groups_2 = [], []
            pnns1, pnns2 = None, None
            
        else :
            pnns_groups_1 = pnns_groups_options(data, country, "pnns_groups_1")

            # Depending of pnns_groups_1 value
            if pnns1 != None:
                pnns_groups_2 = pnns_groups_options(data, country, "pnns_groups_2", pnns1)

                # Reset dropdown 
                if ctx.triggered_id == "dropdown_pnns1":
                    pnns2 = None
            else : 
                pnns_groups_2 = []
            
    # Reset dropdown pnns_groups_2 because they are not the same groups
    elif ctx.triggered_id == "dropdown_pnns1":
        
        pnns2 = None
        
        if pnns1 != None:
            pnns_groups_1 = dash.no_update
            pnns_groups_2 = pnns_groups_options(data, country, "pnns_groups_2", pnns1)
            
        else :
            pnns_groups_2 = []
        
    else:  
        pnns_groups_1 = dash.no_update
        pnns_groups_2 = dash.no_update
    
    # We verify the pnns1 and pnns2 values
    if pnns1 == []:
        pnns1 = None
    if pnns2 == []:
        pnns2 = None
        
    return pnns_groups_1, pnns_groups_2, pnns1, pnns2

    
@app.callback(
    *[
    Output(f"{slide}", property)
    for slide in slider_trigger
    for property in ['min', 'max', 'marks', 'value']
    ],
    Input('intermed_slide_file', 'data'),
    Input('reset_sliders_button', 'n_clicks'),
    prevent_initial_call=True,
)
def update_sliders(df_inter_slide, n_clicks):
            
    # If we change the data
    if (df_inter_slide != None) & (ctx.triggered_id == "intermed_slide_file" or 
                                   ctx.triggered_id == "reset_sliders_button"):

        df_inter_slide = pd.read_json(StringIO(df_inter_slide), orient='split')
        output_values = []
        
        # Rounding down
        for nutrient in ["energy_100g"] + nutrients:
            nutrient_min = math.floor(df_inter_slide[f'{nutrient}'].min())
            nutrient_max = math.ceil(df_inter_slide[f'{nutrient}'].max())
            nutrient_marks = {nutrient_min: str(nutrient_min), nutrient_max: str(nutrient_max)}
            output_values.extend([nutrient_min, nutrient_max, nutrient_marks, [math.floor(nutrient_min), math.ceil(nutrient_max)]])

        return tuple(output_values)

    return dash.no_update

@app.callback(
    Output('search_bar', 'options'),
    Output('search_bar', 'value'),
    Output('table_products', 'selected_rows'),
    Output('table_products', 'style_data_conditional'),
    Output('table_products', 'data'),
    Output('selected_product_table', 'data'),
    Output('dropdown_search_bar_number', 'data'),
    Output('dropdown_table_number', 'data'),
    
    Input('search_bar', 'value'),
    Input('table_products', 'selected_rows'),
    Input('table_products', 'sort_by'),
    Input('sliced_file', 'data'),
    Input('intermed_slide_file', 'data'),
    
    State('table_products', 'data'),
    State('selected_product_table', 'data'),
    State('dropdown_search_bar_number', 'data'),
    State('dropdown_table_number', 'data'),
    
    prevent_initial_call=True,
)

def search_bar_and_table(search_bar_values, selected_row_ids, sort_by, 
                         sliced_file, df_inter_slide, dash_table, dash_table_selected, search_bar_count, table_count):
    # Verification of data
    if (sliced_file == None) or (df_inter_slide == None):
        return [], [], [], [], [], None, 0, 0
    
    # Coloring row and columns, depending of selection or sort_by
    style_data_conditional = []
    if dash_table_selected != None:
        dash_table_selected = pd.read_json(StringIO(dash_table_selected), orient='split')
    else:
        dash_table_selected = None                                   
    
    if ctx.triggered_id in ['sliced_file', 'search_bar', 'table_products']:
        search_bar_option = dash.no_update
        
        df_dash_table = pd.read_json(StringIO(sliced_file), orient='split')
        
        df_dash_table = sorting_df(df_dash_table, sort_by)
        
        # We take the best 20
        df_dash_table = df_dash_table[:20]
    
    elif ctx.triggered_id == 'intermed_slide_file':
        # If we change pnns or country group, we change the bar_option
        df = pd.read_json(StringIO(df_inter_slide), orient='split')
        
        search_bar_option = sorted(df.product_name.unique())
        
        df = sorting_df(df, sort_by)
        
        # We take the best 20
        dash_table = df[:20].to_dict('records')
        
        # Initialization 
        dash_table_selected = None
        search_bar_count = 0
        table_count = 0
        selected_row_ids = []
        search_bar_values = []
        
    if ctx.triggered_id == 'sliced_file':
        if isinstance(dash_table_selected, pd.DataFrame): 
            df_dash_table = pd.concat([df_dash_table, dash_table_selected]).drop_duplicates(keep='first')
            df_dash_table = sorting_df(df_dash_table, sort_by)
            
            concat = pd.concat([df_dash_table.reset_index().drop("index", axis = 1), dash_table_selected])
            selected_row_ids = concat[concat.duplicated(keep="last")].index
        
    # If we manipulate the search bar value, we change the selected_rows
    elif ctx.triggered_id in ['search_bar', 'table_products']:
        # We actualise the selected row in the dash table
        if len(search_bar_values) > 0 or len(selected_row_ids) > 0:
            # We need to extract the data from the bigger file
            df = pd.read_json(StringIO(df_inter_slide), orient='split')
            df = df[df.product_name.isin(search_bar_values)]
            
            # New table
            df_dash_table = pd.concat([df_dash_table, df]).drop_duplicates(keep='first')
            df_dash_table = sorting_df(df_dash_table, sort_by)
            
            # Updating dash_table_selected by adding/deleting depending of user 
            if isinstance(dash_table_selected, pd.DataFrame): 
                # Modification by the search bar
                if ctx.triggered_id == 'search_bar':
                    dash_table_selected = pd.concat([df, dash_table_selected])
                    
                    if (len(search_bar_values) < search_bar_count):
                        dash_table_selected = dash_table_selected[dash_table_selected.duplicated(keep="first")]

                    elif (len(search_bar_values) > search_bar_count):
                        dash_table_selected = dash_table_selected.drop_duplicates(keep='first')
                
                    else :
                        print("No change, shoudn't happen")
                        
                    concat = pd.concat([df_dash_table.reset_index().drop("index", axis = 1), dash_table_selected])

                    selected_row_ids = concat[concat.duplicated(keep="last")].index
                
                # Modification by the table (discounting any sort_by)
                elif ctx.triggered_id == 'table_products':
                    if (len(selected_row_ids) != table_count):
                        dt = df_dash_table.reset_index().drop("index", axis = 1)
                        dash_table_selected = dt[dt.index.isin(selected_row_ids)]

                        # Updating search_bar_values
                        search_bar_values = sorted(dt.loc[dt.index.isin(selected_row_ids), "product_name"].unique())
                
                
            # Replace with the basic
            else:
                if ctx.triggered_id == 'search_bar':
                    dash_table_selected = copy.copy(df)
                    concat = pd.concat([df_dash_table.reset_index().drop("index", axis = 1), dash_table_selected])
                    selected_row_ids = concat[concat.duplicated(keep="last")].index
                    
                elif ctx.triggered_id == 'table_products':
                        dt = df_dash_table.reset_index().drop("index", axis = 1)
                        dash_table_selected = dt[dt.index.isin(selected_row_ids)]
                        search_bar_values = sorted(dt.loc[dt.index.isin(selected_row_ids), "product_name"].unique())
                
            search_bar_count = len(search_bar_values)
            table_count = len(selected_row_ids)
            
        # No product selected
        else : 
            dash_table_selected = None
            search_bar_count = 0
            table_count = 0
    
    else:
        style_data_conditional = row_coloring(dash_table, selected_row_ids, style_data_conditional)
        style_data_conditional = col_coloring(sort_by, style_data_conditional)
        
        return (search_bar_option, search_bar_values, selected_row_ids, style_data_conditional, 
            dash_table, dash_table_selected, search_bar_count, table_count)
    
    if isinstance(df_dash_table, pd.DataFrame): 
        dash_table = df_dash_table.to_dict('records')
    
    style_data_conditional = row_coloring(dash_table, selected_row_ids, style_data_conditional)
    style_data_conditional = col_coloring(sort_by, style_data_conditional)

    if isinstance(dash_table_selected, pd.DataFrame):         
        dash_table_selected = dash_table_selected.to_json(orient='split')
    
    return (search_bar_option, search_bar_values, selected_row_ids, style_data_conditional, 
            dash_table, dash_table_selected, search_bar_count, table_count)
    
@app.callback(
    
    Output('table_products', 'sort_by'),
    Output('dropdown_diet', 'value'),
    Output('dropdown_diet', 'options'),
    Output('personnalized_sorting', 'data'),
    
    Input('dropdown_diet', 'value'),
    Input('table_products', 'sort_by'),
    
    State('personnalized_sorting', 'data'),
)

def diet_controling(diet, sort_by, customized_sorting):

    type_diet={
        "Healthier foods": [
            {'column_id': 'nutriscore_score', 'direction': 'asc'},
            {'column_id': 'fiber_100g', 'direction': 'desc'}
        ],
        "Low sugar foods": [
            {'column_id': 'carbohydrates_100g', 'direction': 'asc'},
            {'column_id': 'nutriscore_score', 'direction': 'asc'}
        ],
        "Protein rich foods": [
            {'column_id': 'proteins_100g', 'direction': 'desc'},
            {'column_id': 'nutriscore_score', 'direction': 'asc'}
        ],
        "Energy rich foods": [
            {'column_id': 'energy_100g', 'direction': 'desc'},
            {'column_id': 'nutriscore_score', 'direction': 'asc'}
        ],
        "Low fat foods": [
            {'column_id': 'fat_100g', 'direction': 'asc'},
            {'column_id': 'nutriscore_score', 'direction': 'asc'}
        ],
        "": [],
        None: [],
        "Customized_sorting": customized_sorting,
              }
    
    if ctx.triggered_id == "table_products":
        if len(sort_by) != 0:
            # When we do the sorting manually, it priorize this order
            customized_sorting = [
                {'column_id': col['column_id'], 'direction': col['direction']}
                for col in sort_by[:-1]
                ]
            customized_sorting.insert(0, {'column_id': sort_by[-1]['column_id'], 
                                          'direction':sort_by[-1]['direction']})

            # We update options_diet
            options_diet = diets + ["Customized_sorting"]
            
            return customized_sorting, "Customized_sorting", options_diet, customized_sorting
        
        # No sorting
        else :
            return [], None, diets, []
            
    return type_diet[diet], dash.no_update, dash.no_update, dash.no_update
    

@app.callback(
    Output('graph_macronutrients', 'figure'),
    
    Input('dropdown_nutrients', 'value'),
    Input('check_list_graph', 'value'),
    Input('sliced_file', 'data'),
    Input('selected_product_table', 'data'),
    *[Input(f'{slide}', 'value') for slide in slider_trigger],
)
    
# We produce the main graphic depending of several input
def graph_macronutrients(nutrients_choice, ch_list_graph, df_slice, df_selected_product,
                        slide_energy, slide_fat, slide_sat_fat, slide_carbs, 
                         slide_fiber, slide_prot, slide_salt, slide_macro):
    
    sliders = [slide_energy, slide_fat, slide_sat_fat, slide_carbs, slide_fiber, slide_prot, slide_salt, slide_macro]
    
    if df_slice != None :  
        df_slice = pd.read_json(StringIO(df_slice), orient='split')
        # Verification that there is data
        if df_slice.shape[0] > 0 :
          
            if ctx.triggered_id in ["sliced_file", "dropdown_nutrients", "check_list_graph", "selected_product_table"]:
                # We create the figure
                figure_nutrients_radio = create_figure_products(df_slice, nutrients, nutrients_choice, ch_list_graph, df_selected_product) 

                return figure_nutrients_radio
        
            elif ctx.triggered_id in slider_trigger:
                patched_figure = Patch()
            
                if nutrients_choice is not None:
                    nutrients_list = nutrients_choice
                else:
                    nutrients_list = nutrients
                
                product_name_list = [[value] for value in df_slice["product_name"].values]
                # Changing the title 
                patched_figure['layout']['title']['text'] = f'Distribution of macronutrients of selected products [{df_slice.shape[0]}]'
                
                if ch_list_graph in ["Distribution", "Products"]:

                    patched_figure['data'][0]['customdata'] = product_name_list
                    patched_figure['data'][1]['customdata'] = product_name_list * len(nutrients_list)

                    patched_figure['data'][0]['y'] = [value for value in df_slice["energy_100g"].values]
                    patched_figure['data'][1]['x'] = [nut for nut in nutrients_list for value in df_slice[nut].values]
                    patched_figure['data'][1]['y'] = [value for nut in nutrients_list for value in df_slice[nut].values]
                    
                else: 
                    # For modifiying the median values 
                    # theta: nutrients names
                    # r: values
                    # -1: median position in the figure
                    median_df = df_slice[nutrients_list].median()

                    # We repeat the first at the end to close the radarplot
                    values = median_df.values.tolist() + [median_df.values[0]]
                    columns = median_df.index.tolist() + [median_df.index[0]]
                        
                    patched_figure['data'][-1]['theta'] = columns
                    patched_figure['data'][-1]['r'] = values
                    
                    patched_figure['data'][-1]['name']= f'Median of {df_slice.shape[0]} products'
                    
                return patched_figure
            
        else :
            return empty_figure()
    
    # If no country selected, no data to show
    else :
        return empty_figure()
    
# Run the app
if __name__ == '__main__':
    app.run(debug=False)
    