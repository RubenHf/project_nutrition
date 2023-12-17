from dash import html, dcc
from functions.dash_components import generate_button
from frontend.style import return_style16_nd

# We return a Html.Div that contains everything for the picture search page
def generating_image_search_page(translations_init):
        
    return html.Div([
            dcc.Upload([
                    generate_button(html.Strong(translations_init['upload_image']), "upload_img_button", return_style16_nd()),
                ], max_size = 15 * 1024 * 1024, # Maximum file size of 15MB accepted
                   accept=".jpeg, .png, .jpg",  # Accepted file types
                   style={'margin': '0 auto', 'float': 'center'}, id="upload_img_data"),
    
            # To show the uploaded image
            html.Div(id='uploaded_img', style={'margin': '0 auto', 'text-align': 'center', 'width':'100%'}),
            
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