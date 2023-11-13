import dash
from dash import Dash, html, dash_table, dcc, callback, Output, Input, State, ctx, Patch
import pandas as pd
import plotly
import plotly.express as px
import plotly.subplots as sp
from plotly.subplots import make_subplots
import copy
import os
import math
from io import StringIO

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

def fig_graph_nutrients(df_slice, nutrients, nutrients_choice, ch_list_graph) :
    
    # To have Energy and the nutrients on the same graph
    figure_nutrients = make_subplots(specs=[[{"secondary_y": True}]])
    
    if nutrients_choice == []:
        nutrients_choice = None
    
    # No Figure
    if len(ch_list_graph) == 0 :#or country == None:
        return px.box()
    
    elif len(ch_list_graph) == 1:
        if "Distribution" in ch_list_graph :
            figure_nutrients1 = px.box(df_slice, y="energy_100g", hover_data=["product_name"]) 
            figure_nutrients2 = px.box(df_slice, y=nutrients_choice, hover_data=["product_name"]) if nutrients_choice != None else px.box(df_slice, y=nutrients, hover_data=["product_name"])

        elif "Products" in ch_list_graph :
            figure_nutrients1 = px.strip(df_slice, y="energy_100g", hover_data=["product_name"]) 
            figure_nutrients2 = px.strip(df_slice, y=nutrients_choice, hover_data=["product_name"]) if nutrients_choice != None else px.strip(df_slice, y=nutrients, hover_data=["product_name"])                

    elif len(ch_list_graph) == 2:

        figure_nutrients1 = px.box(df_slice, y="energy_100g", hover_data=["product_name"])
        figure_nutrients1.add_trace(px.strip(df_slice, y="energy_100g", hover_data=["product_name"]).data[0])
        figure_nutrients1.update_traces(offsetgroup=0.5)

        figure_nutrients2 = px.box(df_slice, 
                                   y=nutrients_choice, 
                                   hover_data=["product_name"], 
                                   points = False) if nutrients_choice != None else px.box(df_slice, 
                                                      y=nutrients, 
                                                      hover_data=["product_name"], 
                                                      points = False
                                    )
        figure_nutrients2.add_trace(px.strip(df_slice, 
                                             y=nutrients_choice, 
                                             hover_data=["product_name"]
                                    ).data[0] if nutrients_choice != None else px.strip(df_slice, 
                                                y=nutrients, 
                                                hover_data=["product_name"]).data[0])
        figure_nutrients2.update_traces(offsetgroup=0.5)
            
    figure_nutrients1.update_traces(marker = dict(color = "red"))
    figure_nutrients2.update_traces(marker = dict(color = "green"))

    for i in range(len(figure_nutrients1.data)):
        figure_nutrients.add_trace(figure_nutrients1.data[i], secondary_y=False)
        figure_nutrients.add_trace(figure_nutrients2.data[i], secondary_y=True)

    # Update of figure layout
    figure_nutrients.update_layout(
        yaxis_title="g/100g",
        title=dict(text=f'Distribution of macronutrients of selected products [{df_slice.shape[0]}]',
                   font=dict(size=24, color="black"), x=0.5, xanchor='center'),
        font=dict(size=18, color="black"),
    )

    # Set y-axes titles
    figure_nutrients.update_yaxes(title_text="g/100g (energy)", secondary_y=False)
    figure_nutrients.update_yaxes(title_text="g/100g (nutrients)", secondary_y=True) 
    # Set x-axe ticks
    figure_nutrients.update_xaxes(ticktext=["energy_100g"] + nutrients, tickvals=[i for i in range(len(nutrients) + 1)])
                                  #range = [0, 100], tickmode="sync")
                                  
    
    return figure_nutrients

##### Initialize the app - incorporate css
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)

server = app.server

app.title = 'Nutrition app'

versionning = "version: 0.4.1"

products_availability = "Referenced products: " + str(data.shape[0])

nutrients = ["fat_100g", "saturated-fat_100g", "carbohydrates_100g", "fiber_100g", "proteins_100g", "salt_100g", "macronutrients_100g"]

slider_trigger = ["slider_energy", "slider_fat", "slider_saturated", "slider_carbohydrates", "slider_fiber", "slider_proteins", "slider_salt", "slider_macronutrients"]

# Default setup
default_country, default_pnns1, default_pnns2 = "France", "Fruits and vegetables", "Soups"

# Options setup for dropdown of countries
c1 = [country.split(",") for country in data.countries_en.unique()]
c2 = [count for country in c1 for count in country]
unique_countries = sorted(list(set(c2)))

unique_countries = [
    {
        'label': f"{country} [{data[data.countries_en.str.contains(country)].shape[0]} products]",
        'value': country
    } 
    for country in unique_countries
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
    ], style={'margin': 'auto', 'width': '33%'}),
    
    # Dropdown for the pnns_groups_1
    html.Div([
        generate_dropdown(default_pnns1, [], "Choose a PNNS group 1", False, 'dropdown_pnns1')
    ], style={'display': 'inline-block', 'width': '50%'}),
    
    # Dropdown for the pnns_groups_2
    html.Div([
        generate_dropdown(default_pnns2, [], "Choose a PNNS group 2", False, 'dropdown_pnns2')
    ], style={'display': 'inline-block', 'width': '50%'}),
        
    # Dropdown for the macronutrient
    html.Div([
        generate_dropdown(None, nutrients, "Choose nutrients", True, 'dropdown_nutrients')
    ], style={'margin': 'auto'}),
    
    # Searchbar products
    html.Div([
        generate_dropdown(None, [], "Search a product", True, 'search_bar')
    ], style={'margin': 'auto'}),
    
    # Checklist type of graph
    html.Div([
        dcc.Checklist(
            value=["Distribution"],
            options=["Distribution", "Products"],
            style={'textAlign': 'center', 'color': 'black', 'fontSize': 15, 'width': '100%'},
            inline=True,
            id='check_list_graph')
    ], style={'margin': 'auto'}),
    
    html.Div([
        # Graph showing the distribution of the nutrients compare to the produce
        html.Div([
            dcc.Graph(id="graph_macronutrients", style={'height': '600px', 'width': '100%', 'float': 'left'}),
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
                page_size = 20,
                sort_action='native',
                sort_mode='multi',
                sort_by=[{'column_id':'nutriscore_score', 'direction':'asc'}], 
                id = "table_products"))
    ], style={'width': '100%'}),
    
    dcc.Store(id='initial_file', data=None),
    dcc.Store(id='intermed_file', data=None),
    dcc.Store(id='intermed_slide_file', data=None),
    dcc.Store(id='sliced_file', data=None),
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
    
    Input('intermed_slide_file', 'data'),
    prevent_initial_call=True,
)

def search_bar_options(df_inter_slide):
    if df_inter_slide is not None :
        
        df_inter_slide = pd.read_json(StringIO(df_inter_slide), orient='split')
        
        # Extract the "product_name" values, get unique sorted values and sort them
        search_bar_options = df_inter_slide.product_name.sort_values().unique()
        return search_bar_options
    
    else :
        return dash.no_update

@app.callback(
    Output('table_products', 'data'),
    Output('table_products', 'style_data_conditional'),
    
    Input('table_products', "sort_by"),
    Input('sliced_file', 'data'),
    Input('search_bar', 'value'),
    
    State('intermed_slide_file', 'data')
)

def table_showing(sort_by, df_slice, search_bar_values, df_inter_slide):
        
    if df_slice != None :
        df_slice = pd.read_json(StringIO(df_slice), orient='split')

        # If we sort the table, we want the 20 best 
        if len(sort_by):
            df_slice.sort_values(
                [col['column_id'] for col in sort_by],
                ascending=[
                    col['direction'] == 'asc'
                    for col in sort_by
                ],
                inplace=True)        
        
        # We show selected products
        if search_bar_values != None:
            df_inter_slide = pd.read_json(StringIO(df_inter_slide), orient='split')
            # We search for the selected products 
            df_inter_slide = df_inter_slide.loc[df_inter_slide.product_name.isin(search_bar_values)]
            
            # We don't show 2 times the same items
            df_slice = df_slice.loc[~df_slice.product_name.isin(search_bar_values)]
            
            # We concat the 20 best total (We retracte to 20 th number selected)
            if len(df_inter_slide) < 21 :
                concat_df = pd.concat([df_inter_slide, df_slice[:20 - len(df_inter_slide)]])
            else :
                concat_df = df_inter_slide

            concat_df.sort_values(
                [col['column_id'] for col in sort_by],
                ascending=[
                    col['direction'] == 'asc'
                    for col in sort_by
                ],
                inplace=True)
            
            # We gather the index 
            concat_df.reset_index(inplace=True, drop=True)
            concat_index = concat_df[concat_df['product_name'].isin(search_bar_values)].index.tolist()

            style_data_conditional = []
            for row in concat_index:
                style_data_conditional.append({
                    'if': {'row_index': row},
                    'backgroundColor': "tomato" if row >= len(df_slice[:20 - len(df_inter_slide)]) else "green",
                    'color': 'white'
                })
        
            return concat_df.to_dict('records'), style_data_conditional
        
        else :
            return df_slice[:20].to_dict('records'), []
    
    # If no country selected, no data to show
    else : 
        return None, []

@app.callback(
    Output('graph_macronutrients', 'figure'),
    
    Input('dropdown_nutrients', 'value'),
    Input('check_list_graph', 'value'),
    Input('sliced_file', 'data'),
    *[Input(f'{slide}', 'value') for slide in slider_trigger],
)
    
# We produce the main graphic depending of several input
def graph_macronutrients(nutrients_choice, ch_list_graph, df_slice,
                        slide_energy, slide_fat, slide_sat_fat, slide_carbs, 
                         slide_fiber, slide_prot, slide_salt, slide_macro):
    
    sliders = [slide_energy, slide_fat, slide_sat_fat, slide_carbs, slide_fiber, slide_prot, slide_salt, slide_macro]

    if df_slice != None :
        df_slice = pd.read_json(StringIO(df_slice), orient='split')
        # Verification that
        if df_slice.shape[0] > 1 :
            if ctx.triggered_id in ["sliced_file", "dropdown_nutrients", "check_list_graph"]:
            
                return fig_graph_nutrients(df_slice, nutrients, nutrients_choice, ch_list_graph) 
        
            elif ctx.triggered_id in slider_trigger:
                patched_figure = Patch()
            
                if nutrients_choice is not None:
                    nutrients_list = nutrients_choice
                else:
                    nutrients_list = nutrients
            
                product_name_list = [[value] for value in df_slice["product_name"].values]

                patched_figure['data'][0]['customdata'] = product_name_list
                patched_figure['data'][1]['customdata'] = product_name_list * len(nutrients_list)

                patched_figure['data'][0]['y'] = [value for value in df_slice["energy_100g"].values]
                patched_figure['data'][1]['x'] = [nut for nut in nutrients_list for value in df_slice[nut].values]
                patched_figure['data'][1]['y'] = [value for nut in nutrients_list for value in df_slice[nut].values]
                # Changing the title 
                patched_figure['layout']['title']['text'] = f'Distribution of macronutrients of selected products [{df_slice.shape[0]}]'
                
                return patched_figure
            else :
              return px.strip()
    
    # If no country selected, no data to show
    else :
        return px.strip()
    
# Run the app
if __name__ == '__main__':
    app.run(debug=False)
    