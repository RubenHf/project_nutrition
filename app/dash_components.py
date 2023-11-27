from dash import html, dcc

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
                style={'fontFamily': 'monospace', 'align-items': 'center', 'justify-content': 'center', 
                       'textAlign': 'center', 'color': 'black', 'fontSize': 15, 'width': '100%', 'cursor': 'pointer'},
                placeholder=placeholder,
                multi=multi,
                id=id,
                clearable=clearable,
            )

# Function to generate a Button
def generate_button(title_button, id_button, style_button):
    return html.Button(
        title_button, 
        id=id_button, 
        n_clicks=0, 
        style=style_button)
