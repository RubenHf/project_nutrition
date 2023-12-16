from dash import html
from frontend.right_side.advanced_search import generating_advanced_search_page
from frontend.right_side.browser_search import generating_browser_history_page
from frontend.right_side.image_search import generating_image_search_page
from frontend.right_side.image_selection.selected_image import generating_image_selected_page
from frontend.right_side.image_selection.diet_image import generating_image_by_diet_page

def generating_navigation_result(translations_init, initial_language, pnns_groups_1, pnns_groups_2, pnns_groups, diets, nutrients):
    return html.Div([
        # Return a Div containing elements for the advanced search
        generating_advanced_search_page(translations_init, pnns_groups_1, diets),

        # We set an invisible anchor (for navigation purpose)
        html.A(id="top_dash"),

        # We display the description of a selected product (if clicked)
        # We display the result with the different diets
        html.Div([
            # To display a selected product at the top
            generating_image_selected_page(translations_init),
            # To display the list of products in different diets
            generating_image_by_diet_page(translations_init, diets, nutrients, initial_language),
        ], style={'display': 'block', 'flex-direction': 'row', 'width': '100%'},  id='images_gestion'),

        # Return a Div containing elements for the browser history 
        generating_browser_history_page(),
        
        # We set an invisible anchor (for navigation purpose)
        html.A(id="search_by_image"),
        generating_image_search_page(translations_init),
            
    ], style={'flex-direction': 'row', 'width': '100%', 'background-color': '#F0F0F0', 
              'overflowY': 'scroll', 'height': '100vh', 'flex': '2'})