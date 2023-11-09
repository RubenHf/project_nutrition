import dash
from dash import Dash, html, dash_table, dcc, callback, Output, Input, State, ctx, Patch
import pandas as pd
import plotly
import plotly.express as px
import plotly.subplots as sp
from plotly.subplots import make_subplots
import copy
import os

# Get the directory of the script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Go up one level to the parent directory (assuming the script is in the 'app' directory)
app_dir = os.path.dirname(script_dir)

# Define the path to the file in the /files directory
file_path = os.path.join(app_dir, 'files', 'donnees_nettoyees.csv')
print(file_path)
# Now you can use the file_path to access your file
with open(file_path, 'r') as file:
    data = pd.read_csv(file_path, sep = "\t")


##### Initialize the app - incorporate css
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)

server = app.server

app.title = 'Nutrition app'

versionning = "version: 0.0.1"

products_availability = "Referenced products: " + str(data.shape[0])

nutrients = ["fat_100g", "saturated-fat_100g", "carbohydrates_100g", "fiber_100g", "proteins_100g", "salt_100g", "Macronutrients"]

# Default setup
default_country, default_pnns1, default_pnns2 = "France", "Fruits and vegetables", "Soups"

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
    
    html.Div([
        dcc.Dropdown(
            value=default_country,
            style={'textAlign': 'left', 'color': 'black', 'fontSize': 15, 'width': '100%'},
            placeholder="Choose a country",
            multi=False,
            id='dropdown_country')
    ], style={'margin': 'auto', 'width': '33%'}),
    
    # Dropdown for the pnns_groups_1
    html.Div([
        dcc.Dropdown(
            value=default_pnns1, 
            style={'textAlign': 'left', 'color': 'black', 'fontSize': 15, 'width': '100%'},
            placeholder="Choose a PNNS group 1",
            multi=False,
            id='dropdown_pnns1')
    ], style={'display': 'inline-block', 'width': '50%'}),
    
    # Dropdown for the pnns_groups_2
    html.Div([
        dcc.Dropdown(
            value=default_pnns2,
            style={'textAlign': 'left', 'color': 'black', 'fontSize': 15, 'width': '100%'},
            placeholder="Choose a PNNS group 2",
            multi=False,
            id='dropdown_pnns2')
    ], style={'display': 'inline-block', 'width': '50%'}),
        
    # Dropdown for the macronutrient
    html.Div([
        dcc.Dropdown(
            value=None,
            options=nutrients,
            style={'textAlign': 'left', 'color': 'black', 'fontSize': 15, 'width': '100%'},
            placeholder="Show nutrients",
            multi=True,
            id='dropdown_nutrients')
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
            html.Div(["Energy kcal/100g",
            dcc.RangeSlider(0, 3880, 10, value=[0, 3880], marks={0:"0", 3880:"3880"}, id='slider_energy',
                           tooltip={"placement": "bottom", "always_visible": True})
                     ], style={'textAlign': 'center', 'color': 'black', 'fontSize': 15}),
            html.Div(["Fat g/100g",
            dcc.RangeSlider(0, 100, 1, value=[0, 100], marks={0:"0", 100:"100"}, id='slider_fat',
                           tooltip={"placement": "bottom", "always_visible": True})
                     ], style={'textAlign': 'center', 'color': 'black', 'fontSize': 15}),
            html.Div(["Saturated_fat g/100g",
            dcc.RangeSlider(0, 100, 1, value=[0, 100], marks={0:"0", 100:"100"}, id='slider_saturated',
                           tooltip={"placement": "bottom", "always_visible": True})
                     ], style={'textAlign': 'center', 'color': 'black', 'fontSize': 15}),
            html.Div(["Carbohydrates g/100g",
            dcc.RangeSlider(0, 100, 1, value=[0, 100], marks={0:"0", 100:"100"}, id='slider_carbohydrates',
                           tooltip={"placement": "bottom", "always_visible": True})
                     ], style={'textAlign': 'center', 'color': 'black', 'fontSize': 15}),
            html.Div(["Fiber g/100g",
            dcc.RangeSlider(0, 100, 1, value=[0, 100], marks={0:"0", 100:"100"}, id='slider_fiber',
                           tooltip={"placement": "bottom", "always_visible": True})
                     ], style={'textAlign': 'center', 'color': 'black', 'fontSize': 15}),
            html.Div(["Proteins g/100g",
            dcc.RangeSlider(0, 100, 1, value=[0, 100], marks={0:"0", 100:"100"}, id='slider_proteins',
                           tooltip={"placement": "bottom", "always_visible": True})
                     ], style={'textAlign': 'center', 'color': 'black', 'fontSize': 15}),
            html.Div(["Salt g/100g",
            dcc.RangeSlider(0, 100, 1, value=[0, 100], marks={0:"0", 100:"100"}, id='slider_salt',
                           tooltip={"placement": "bottom", "always_visible": True})
                     ], style={'textAlign': 'center', 'color': 'black', 'fontSize': 15}),
            html.Div(["Macronutrients g/100g",
            dcc.RangeSlider(0, 100, 1, value=[0, 100], marks={0:"0", 100:"100"}, id='slider_macronutrients',
                           tooltip={"placement": "bottom", "always_visible": True})
                     ], style={'textAlign': 'center', 'color': 'black', 'fontSize': 15}),
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
    ], style={'width': '100%'})
    
])



@app.callback(
    Output('dropdown_country','options'),
    Output('dropdown_country','value'),
    
    Input('dropdown_country','value'),
)

# We define the countries list
def choice_country(country):
    c1 = [country.split(",") for country in data.countries_en.unique()]
    c2 = [count for country in c1 for count in country]
    unique_countries = sorted(list(set(c2)))
    
    if country == []:
        country = None
        
    return unique_countries, country
    
@app.callback(
    Output('dropdown_pnns1','options'),
    Output('dropdown_pnns2','options'),
    Output('dropdown_pnns1','value'),
    Output('dropdown_pnns2','value'),
    
    Input('dropdown_pnns1','value'),
    Input('dropdown_pnns2','value'),
)

# We define the pnns_groups
def choice_pnns_groups(pnns1, pnns2):
    pnns_groups_1 = data.pnns_groups_1.unique()
    
    # Depending of pnns_groups_1 value
    if pnns1 != None :
        pnns_groups_2 = data.loc[data.pnns_groups_1 == pnns1, "pnns_groups_2"].unique()
        # Reset dropdown 
        if ctx.triggered_id == "dropdown_pnns1":
            pnns2 = None
    else : 
        pnns_groups_2 = []
        
    if pnns1 == []:
        pnns1 = None
    if pnns2 == []:
        pnns2 = None
        
    return pnns_groups_1, pnns_groups_2, pnns1, pnns2

@app.callback(
    Output('slider_energy', 'value'),
    Output('slider_fat', 'value'),
    Output('slider_saturated', 'value'),
    Output('slider_carbohydrates', 'value'),
    Output('slider_fiber', 'value'),
    Output('slider_proteins', 'value'),
    Output('slider_salt', 'value'),
    Output('slider_macronutrients', 'value'),
    
    Input('reset_sliders_button', 'n_clicks'),
)

def reset_sliders_button(button_reset):
    return [0, 3880], [0, 100], [0, 100], [0, 100], [0, 100], [0, 100], [0, 100], [0, 100]

@app.callback(
    Output('table_products', 'data'),
    
    Input('dropdown_pnns1', 'value'),
    Input('dropdown_pnns2', 'value'),
    Input('dropdown_country','value'),
    Input('slider_energy', 'value'),
    Input('slider_fat', 'value'),
    Input('slider_saturated', 'value'),
    Input('slider_carbohydrates', 'value'),
    Input('slider_fiber', 'value'),
    Input('slider_proteins', 'value'),
    Input('slider_salt', 'value'),
    Input('slider_macronutrients', 'value'),
    Input('table_products', "sort_by"),
)

def table_showing(pnns1, pnns2, country, 
                         slide_energy, slide_fat, slide_sat_fat, slide_carbs, 
                         slide_fiber, slide_prot, slide_salt, slide_macro,
                         sort_by):

    sliders = [slide_energy, slide_fat, slide_sat_fat, slide_carbs, slide_fiber, slide_prot, slide_salt, slide_macro]

    df = copy.copy(data)
    df = df.loc[(df.countries_en.str.contains(country))
                  &(df.pnns_groups_1==pnns1)]
    if pnns2 != None :
        df = df.loc[df.pnns_groups_2==pnns2]
    
    # If we modify one of the slider
    if ctx.triggered_id in ['slider_energy', 'slider_fat', 'slider_saturated', 'slider_carbohydrates', 
                            'slider_fiber', 'slider_proteins', 'slider_salt', 'slider_macronutrients']:
    
        for nut, slide in zip(["energy_100g"]+nutrients, sliders):
            df = df.loc[(df[nut] >= slide[0]) & (df[nut] <= slide[1])]
    if len(sort_by):
        df.sort_values(
            [col['column_id'] for col in sort_by],
            ascending=[
                col['direction'] == 'asc'
                for col in sort_by
            ],
            inplace=True
        )

    return df.iloc[:20, :].to_dict('records')

@app.callback(
    Output('graph_macronutrients', 'figure'),
    
    Input('dropdown_pnns1', 'value'),
    Input('dropdown_pnns2', 'value'),
    Input('dropdown_country','value'),
    Input('dropdown_nutrients', 'value'),
    Input('slider_energy', 'value'),
    Input('slider_fat', 'value'),
    Input('slider_saturated', 'value'),
    Input('slider_carbohydrates', 'value'),
    Input('slider_fiber', 'value'),
    Input('slider_proteins', 'value'),
    Input('slider_salt', 'value'),
    Input('slider_macronutrients', 'value'),
    Input('check_list_graph', 'value'),
)

# We produce the main graphic deepending of several input
def graph_macronutrients(pnns1, pnns2, country, nutrients_choice, 
                         slide_energy, slide_fat, slide_sat_fat, slide_carbs, 
                         slide_fiber, slide_prot, slide_salt, slide_macro,
                         ch_list_graph
                        ):    
   
    sliders = [slide_energy, slide_fat, slide_sat_fat, slide_carbs, slide_fiber, slide_prot, slide_salt, slide_macro]
    mask = copy.copy(data)
    
    # To have Energy and the nutrients on the same graph
    figure_nutrients = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Sliders controlers
    for nut, slide in zip(["energy_100g"]+nutrients, sliders):
        mask = mask.loc[(mask[nut] >= slide[0]) & (mask[nut] <= slide[1])]

    if nutrients_choice == []:
        nutrients_choice = None
    
    # No Figure
    if len(ch_list_graph) == 0 or country == None:
        return px.box()
    
    if country != None :
        mask = mask.loc[mask.countries_en.str.contains(country)]
        if pnns1 != None:
            if pnns2 != None:
                mask = mask.loc[(mask.pnns_groups_1 == pnns1) & (mask.pnns_groups_2 == pnns2)]
            else :
                mask = mask.loc[mask.pnns_groups_1 == pnns1]
        if len(ch_list_graph) == 1:
            if "Distribution" in ch_list_graph :
                figure_nutrients1 = px.box(mask, y="energy_100g", hover_data=["product_name"]) 
                #figure_nutrients2 = px.box()
                #for nut in nutrients:
                 #   figure_nutrients2.add_traces(px.box(mask, y=nut).data[0])
                figure_nutrients2 = px.box(mask, y=nutrients_choice, hover_data=["product_name"]) if nutrients_choice != None else px.box(mask, y=nutrients, hover_data=["product_name"])

            elif "Products" in ch_list_graph :
                figure_nutrients1 = px.strip(mask, y="energy_100g", hover_data=["product_name"]) 
                figure_nutrients2 = px.strip(mask, y=nutrients_choice, hover_data=["product_name"]) if nutrients_choice != None else px.strip(mask, y=nutrients, hover_data=["product_name"])                
                
        elif len(ch_list_graph) == 2:
            
            figure_nutrients1 = px.box(mask, y="energy_100g", hover_data=["product_name"])
            figure_nutrients1.add_trace(px.strip(mask, y="energy_100g", hover_data=["product_name"]).data[0])
            figure_nutrients1.update_traces(offsetgroup=0.5)
            
            figure_nutrients2 = px.box(mask, 
                                       y=nutrients_choice, 
                                       hover_data=["product_name"], 
                                       points = False) if nutrients_choice != None else px.box(mask, 
                                                          y=nutrients, 
                                                          hover_data=["product_name"], 
                                                          points = False
                                        )
            figure_nutrients2.add_trace(px.strip(mask, 
                                                 y=nutrients_choice, 
                                                 hover_data=["product_name"]
                                        ).data[0] if nutrients_choice != None else px.strip(mask, 
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
            title=dict(text="Distribution of macronutrients of selected products",
                       font=dict(size=24, color="black"), x=0.5, xanchor='center'),
            font=dict(size=18, color="black")
        )
        # Set y-axes titles
        figure_nutrients.update_yaxes(title_text="g/100g (energy)", secondary_y=False)
        figure_nutrients.update_yaxes(title_text="g/100g (nutrients)", secondary_y=True)
     

    return figure_nutrients
    
# Run the app
if __name__ == '__main__':
    app.run(debug=False)
    