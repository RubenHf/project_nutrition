from dash import html, dcc, dash_table

 # Function to generate a RangeSlider
def generate_slider(title, id_dcc, max_value):
    return html.Div([title,
                     dcc.RangeSlider(0, max_value, 1, value=[0, max_value],
                                    marks={0: "0", max_value: str(max_value)},
                                    id=id_dcc,
                                    tooltip={"placement": "bottom", "always_visible": True})
                     ], style={'textAlign': 'center', 'color': 'black', 'fontSize': 15})


# Function to generate a DropDown
def generate_dropdown(value, options, placeholder, multi, id_dcc, clearable = True):
    return dcc.Dropdown(
                value=value,
                options=options,
                style={'fontFamily': 'monospace', 'align-items': 'center', 'justify-content': 'center', 
                       'textAlign': 'center', 'color': 'black', 'fontSize': 15, 'width': '100%', 'cursor': 'pointer'},
                placeholder=placeholder,
                multi=multi,
                id=id_dcc,
                clearable=clearable,
            )
def generate_input(placeholder, id_dcc, type_dcc = "text"):
    return dcc.Input(
                style={'fontFamily': 'monospace', 'align-items': 'center', 'justify-content': 'center', 
                       'textAlign': 'center', 'color': 'black', 'fontSize': 15, 'width': '100%'},
                placeholder=placeholder,
                type=type_dcc,
                id=id_dcc,
            )

# Function to generate a button
def generate_button(title_button, id_button, style_button):
    return html.Button(
        title_button, 
        id=id_button, 
        n_clicks=0, 
        style=style_button)

# Function to generate a Dash table
def generate_table(df, page_size, id_table):
    return dash_table.DataTable(
        data=df,
        columns=None,
        page_size = page_size,
        style_as_list_view=True,
        style_header={'fontWeight': 'bold', 'color': 'black'},
        style_table={'overflowY': 'auto'},
        row_selectable='single',
        selected_rows=[],
        style_cell={
            'textAlign': 'center',
            'height': 'auto',
            'whiteSpace': 'normal'
        },
        id = id_table),

# Function to generate a radio item
def generate_radio_items(options, default, id_radio, inline = True):
    return dcc.RadioItems(
        value=default,
        options=[
            {'label': label, 'value': label} 
            for label in options
        ],
        inline=inline,
        id=id_radio,
        style={'textAlign': 'center', 'color': 'black', 'fontSize': 15, 'width': '100%'}
    )
