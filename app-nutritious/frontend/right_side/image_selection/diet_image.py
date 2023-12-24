from dash import html, dcc, get_asset_url
from frontend.style import return_style24

# We return a Html.Div that contains everything for the products caracteristics and images
def generating_image_by_diet_page(translations_init, diets, nutrients, initial_language):
    return html.Div([
        # Title at the top
        html.Div(id='images_title', style=return_style24()),

        # Generate images and textes
        generate_images_and_textes(translations_init, diets),
    ])

# We return a Html.Div constituated of:
# Title of the diet
# Images of each products
# Texte below the images
def generate_images_and_textes(translations_init, diets):
    return html.Div([
                html.Div([
                    html.Button(children=f"{diet}", id=f"{diet}_div", n_clicks=0,
                                style={'font-size': '16px', 'color': 'black', 'textAlign': 'left', 'margin': '0px',
                                       'border': '1px', 'background-color': 'lightgray', 'width': '100%', 'margin': 'auto'}),
                    html.Div([
                        html.Div([
                           # dcc.Loading(id=f"loading_section_{diet}_img_{i}", type="default", children = [
                            # html.A for having the clickable action on and going back to top
                            html.A( 
                                html.Img(id=f"{diet}_img_{i}", src=get_asset_url('no_image.jpg'), n_clicks = 0, 
                                     alt=translations_init['no_image_available'], style={'height': '200px', 'width': '200px'}),
                            href='#top_dash'),
                           #]),
                            html.Div(id=f"{diet}_div_{i}")
                        ], style={'display': 'flex', 'flex-direction': 'column', 'width': '100%'})
                        for i in range(20)
                    ], style={'display': 'flex', 'flex-direction': 'row', 'overflowX': 'scroll'})
                ], style={'display': 'flex', 'flex-direction': 'column', 'width': '100%'})
                for diet in diets
            ])
