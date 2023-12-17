import pandas as pd
import numpy as np
import plotly.express as px
from plotly.subplots import make_subplots
from io import StringIO
from functions.language import get_translate

# We retrieve the language dictionnary
translations = get_translate()

def empty_figure(language):
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
    fig.add_annotation(text=f"{translations[language]['No data to show']}", x=0.5, y=0.5, showarrow=False,
                        font=dict(color="Black", size=20))
    return fig

def blank_figure(language):
    """
        Just creating the template
    """
    nutrients = ["fat_100g", "saturated-fat_100g", "carbohydrates_100g", "fiber_100g", "proteins_100g", "salt_100g", "macronutrients_100g"]

    # To put Energy and the nutrients on the same graph but with differents scales
    figure = make_subplots(specs=[[{"secondary_y": True}]])

    figure_energy = px.violin(box=False) 
    figure_others = px.violin(box=False) 

    figure_others.update_traces(width = 1)
        
    figure_energy.update_traces(marker = dict(color = "red"), hovertemplate='<br>Product name: %{customdata}<br>energy_100g = %{y}')
    figure_others.update_traces(marker = dict(color = "green"), hovertemplate='<br>Product name: %{customdata}<br>%{x}: %{y}')
            
            
    figure_energy_selected = px.strip()
    figure_others_selected = px.strip()
    figure_energy_selected.update_traces(hovertemplate='<br>Product name: %{customdata}<br>energy_100g = %{y}')
    figure_others_selected.update_traces(hovertemplate='<br>Product name: %{customdata}<br>%{x}: %{y}')
            
    for fig in [figure_energy_selected, figure_others_selected]:   
        fig.update_traces(marker = dict(color = "blue"), 
                            marker_size=8, name="Selected", 
                            marker_line_color="black", marker_line_width=2)
                         
    for i in range(len(figure_energy.data)):
        figure.add_trace(figure_energy.data[i], secondary_y=False)
        figure.add_trace(figure_others.data[i], secondary_y=True)
        figure.add_trace(figure_energy_selected.data[i], secondary_y=False)
        figure.add_trace(figure_others_selected.data[i], secondary_y=True)

    # Update of figure layout
    figure.update_layout(
        yaxis_title="g/100g",
        title=dict(text='', font=dict(size=24, color="black"), x=0.5, xanchor='center'),
        font=dict(size=18, color="black"),
        plot_bgcolor='white',
    )

        # Set y-axes titles and background
    figure.update_yaxes(
        title_text=f"g/100g ({translations[language]['energy']})", 
        secondary_y=False,
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='lightgrey')

    figure.update_yaxes(
        title_text=f"g/100g ({translations[language]['nutrients']})", 
        secondary_y=True) 

    # Set x-axe ticks
    figure.update_xaxes(
        ticktext=[translations[language][feat] for feat in ["energy_100g"] + nutrients],
        tickvals=[i for i in range(len(nutrients) + 1)],
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='lightgrey')

    return figure

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
    if df_selected_products is not None:
        if not isinstance(df_selected_products, pd.DataFrame):
            # Assuming df_selected_products is a JSON-formatted string
            df_selected_products = pd.read_json(StringIO(df_selected_products), orient='split')

        if df_selected_products.shape[0] > 0 :
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
        hovertemplate='<br>%{theta} = %{r}' # nutrient = value
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
        
        
        
def create_figure_products(df, list_nutrients, selected_nutrients, 
                           selected_graphical_type, df_selected_products, language):
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
            figure_energy = px.violin(df, y="energy_100g", box=False) 
            figure_others = (px.violin(df, y=selected_nutrients, box=False) 
                             if len(selected_nutrients) > 0 
                             else px.violin(df, y=list_nutrients, box=False))

            figure_others.update_traces(width = 1)

        elif selected_graphical_type == "Products":
            figure_energy = px.strip(df, y="energy_100g") 
            figure_others = (px.strip(df, y=selected_nutrients) 
                                 if len(selected_nutrients) > 0 
                                 else px.strip(df, y=list_nutrients))  
            
        figure_energy['data'][0]['customdata'] = [name for name in df['product_name']]
        if len(selected_nutrients) > 0 :
            figure_others['data'][0]['customdata'] = [name for name in df['product_name']] * len(selected_nutrients)
        else:
            figure_others['data'][0]['customdata'] = [name for name in df['product_name']] * len(list_nutrients)
        
        figure_energy.update_traces(marker = dict(color = "red"), hovertemplate='<br>Product name: %{customdata}<br>energy_100g = %{y}')
        figure_others.update_traces(marker = dict(color = "green"), hovertemplate='<br>Product name: %{customdata}<br>%{x}: %{y}')
                
                         
        if df_selected_products is not None:
            if not isinstance(df_selected_products, pd.DataFrame):
                # Assuming df_selected_products is a JSON-formatted string
                df_selected_products = pd.read_json(StringIO(df_selected_products), orient='split')

            figure_energy_selected = px.strip(df_selected_products, y="energy_100g") 
            figure_others_selected = (px.strip(df_selected_products, y=selected_nutrients) 
                                 if len(selected_nutrients) > 0 
                                 else px.strip(df_selected_products, y=list_nutrients))
            # Putting informations
            figure_energy_selected['data'][0]['customdata'] = [name for name in df_selected_products['product_name']]
            if len(selected_nutrients) > 0:
                figure_others_selected['data'][0]['customdata'] = [name for name in df_selected_products['product_name']] * len(selected_nutrients)
            else:
                figure_others_selected['data'][0]['customdata'] = [name for name in df_selected_products['product_name']] * len(list_nutrients)
            figure_energy_selected.update_traces(hovertemplate='<br>Product name: %{customdata}<br>energy_100g = %{y}')
            figure_others_selected.update_traces(hovertemplate='<br>Product name: %{customdata}<br>%{x}: %{y}')

        else :
            figure_energy_selected = px.strip()
            figure_others_selected = px.strip()
            
        for fig in [figure_energy_selected, figure_others_selected]:   
            fig.update_traces(marker = dict(color = "blue"), 
                                marker_size=8, name="Selected", 
                                marker_line_color="black", marker_line_width=2)
                         
        for i in range(len(figure_energy.data)):
            figure.add_trace(figure_energy.data[i], secondary_y=False)
            figure.add_trace(figure_others.data[i], secondary_y=True)
            figure.add_trace(figure_energy_selected.data[i], secondary_y=False)
            figure.add_trace(figure_others_selected.data[i], secondary_y=True)

        # Update of figure layout
        figure.update_layout(
            yaxis_title="g/100g",
            title=dict(text=f"{translations[language]['Distribution_selected_products']} [{df.shape[0]}]",
                       font=dict(size=24, color="black"), x=0.5, xanchor='center'),
            font=dict(size=18, color="black"),
            plot_bgcolor='white',
        )

        # Set y-axes titles and background
        figure.update_yaxes(
            title_text=f"g/100g ({translations[language]['energy']})", 
            secondary_y=False,
            mirror=True,
            ticks='outside',
            showline=True,
            linecolor='black',
            gridcolor='lightgrey')
                             
        figure.update_yaxes(
            title_text=f"g/100g ({translations[language]['nutrients']})", 
            secondary_y=True) 
                             
        # Set x-axe ticks
        figure.update_xaxes(
            ticktext=[translations[language][feat] for feat in ["energy_100g"] + list_nutrients],
            tickvals=[i for i in range(len(list_nutrients) + 1)],
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
        return empty_figure(language)

def patch_graphic(patched_figure, df_whole, df_product, ch_list_graph, nutrients_list, type_modification, language):
    """
        Function that modify the patch figure
        Take as arguments, the dataframes to use
        The type of figure
        The type of modification (list):
        A: Change for primary data
        B: Change to the product data
        
        Return the patched_figure
    """
    
    #A, B: For the positions in the graph: 1 and 2 are for the whole data, 3 and 4 for the selected produced
    for row in type_modification:
        if row == "A":
            df = df_whole.copy()
            patched_figure['layout']['title']['text'] = f"{translations[language]['Distribution_of']} {df.shape[0]} {translations[language]['products']}"
            A, B = 0, 1

        elif row == "B":
            df = df_product.copy()
            A, B = 2, 3
        
        else:
            continue
        product_name_list = [[value] for value in df["product_name"].values] 
        patched_figure['data'][A]['customdata'] = product_name_list
        patched_figure['data'][B]['customdata'] = product_name_list * len(nutrients_list)

        patched_figure['data'][A]['y'] = [value for value in df["energy_100g"].values]
        patched_figure['data'][B]['x'] = [nut for nut in nutrients_list for value in df[nut].values]
        patched_figure['data'][B]['y'] = [value for nut in nutrients_list for value in df[nut].values]

    return patched_figure


def figure_result_model(df, language):
    """
        Function showing the probabilities (result) of the classification model (pnns1 or pnns2)
    """
    
    df_sorted = df.sort_values("probabilities")
    # To extract the pnns_groups (either 1 or 2) and the probabilities
    categories = list(df_sorted[df.columns[0]])
    probabilities = np.round(df_sorted[df_sorted.columns[1]]*100)

    figure = px.bar(x = probabilities, y = categories, orientation='h')

    # Update figure layout
    figure.update_layout(
                yaxis_title=None, xaxis_title=f"{translations[language]['Probabilities to be correct']} (%)",
                title=dict(text=f"{translations[language]['Probabilities to be correct']}:",
                           font=dict(size=24, color="black"), x=0.5, xanchor='center'),
                font=dict(size=18, color="black"),
                plot_bgcolor='lightgray',
                paper_bgcolor='#F0F0F0',
            )
    figure.update_yaxes(showline=True, linecolor='black', fixedrange=True)
    figure.update_xaxes(showline=True, linecolor='black', range = [0, None], fixedrange=True)

    # Update the hovertemplate information
    figure.update_traces(hovertemplate='<br>Pnns_groups: %{y}<br>Probability: %{x}%')

    return figure