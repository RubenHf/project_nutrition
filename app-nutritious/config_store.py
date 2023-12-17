from dash import dcc

# We return a tupple containing the dcc.Store components
# We initiates the values

def generating_dcc_store(diets, initial_language):
    return (
        dcc.Store(id='sliced_file', data=None),
        dcc.Store(id='personnalized_sorting', data=None),
        dcc.Store(id='pnns1_chosen', data=None),
        dcc.Store(id='pnns2_chosen', data=None),
        dcc.Store(id='search_on', data=False),
        dcc.Store(id='shown_img', data={f'{diet}_img_{i}': None for diet in diets for i in range(20)}),
        # To store the client navigation history
        dcc.Store(id='history', data=[]),
        dcc.Store(id='loading_history', data=False),
        dcc.Store(id='prevent_update', data=False),
        dcc.Store(id='search_bar_data', data=False),
        # To handle session memory
        dcc.Store(id='language_user', data=initial_language)
    )