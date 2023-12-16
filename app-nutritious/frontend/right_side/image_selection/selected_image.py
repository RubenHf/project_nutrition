from dash import html, dcc, get_asset_url
from functions.dash_components import generate_dropdown
from frontend.style import return_style24

# We return a Html.Div that contains everything for the selected picture
def generating_image_selected_page(translations_init):

    return html.Div(id='selected_product_style', style={'display':'None'}, children=[
        dcc.Loading(id="loading_section_img", type="default", children = [
            html.Div(id='selected_product_title',  
                style=return_style24()),

            # Searchbar for products with the same product name
            html.Div([
                generate_dropdown(None, [], translations_init['search_product'], False, 'multiple_product_dropdown')
            ], style={'margin': '0 auto', 'border': '1px solid black'}),
            
            html.Div([
                html.Img(id='selected_product_img', src=get_asset_url('no_image.jpg'), 
                    alt=translations_init['no_image_available'], style = {'height':'450px', 'width':'450px'}),
                html.Div(id='selected_product_texte')
            ], style={'display': 'flex', 'flex-direction': 'row', 'width': '100%'}),

            # To display up to 3 + 1 alternatives images
            html.Div([
                html.A( 
                    html.Img(id=f"selected_img_{i}", src=get_asset_url('no_image.jpg'), n_clicks = 0, 
                            alt=translations_init['no_image_available'], style={'height': '150px', 'width': '150px'}),
                    href='#top_dash')
                for i in range(4)
            ], style={'display': 'flex', 'flex-direction': 'row', 'width': '100%'}),
        ]),
    ])