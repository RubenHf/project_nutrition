@app.callback(
    Output('images_title', 'children'),
    *[Output(f'{diet}_div', 'children') for diet in diets],
    *[Output(f'{diet}_img_{i}', 'src') for diet in diets for i in range(20)],
    *[Output(f'{diet}_img_{i}', 'style') for diet in diets for i in range(20)],
    *[Output(f'{diet}_div_{i}', 'children') for diet in diets for i in range(20)],
    *[Output(f"selected_img_{i}", 'src') for i in range(4)],
    *[Output(f"selected_img_{i}", 'style') for i in range(4)],
    *[Output(f"graphic_gestion_{pos}", 'style') for pos in ['bottom', 'top']],
    *[Output(f"{pos}_button_graphic", 'style') for pos in ['bottom', 'top']],
    Output('personnalized_sorting', 'data', allow_duplicate=True),
    Output("selected_product_style", 'style'),
    Output("selected_product_img", 'src'),
    Output("selected_product_title", 'children'),
    Output("selected_product_texte", 'children'),
    Output('advanced_search_div', 'style', allow_duplicate=True),
    Output('search_on', 'data'),
    Output('shown_img', 'data'),
    Output('history', 'data', allow_duplicate=True),
    Output('multiple_product_dropdown', 'style', allow_duplicate=True),
    Output('browser_history_div', 'style', allow_duplicate=True),
    Output('prevent_update', 'data'),
    Output('pnns1_chosen', 'data', allow_duplicate=True),
    Output('pnns2_chosen', 'data', allow_duplicate=True),
    Output('picture_search_div', 'style', allow_duplicate=True),
    Output('data_figure', 'data'),
    
    *[Input(f'{diet}_div', 'n_clicks') for diet in diets],
    *[Input(f'{diet}_img_{i}', 'n_clicks') for diet in diets for i in range(20)],
    Input('pnns1_chosen', 'data'),
    Input('pnns2_chosen', 'data'),
    Input('dropdown_country','value'),
    Input('search_bar', 'value'),
    Input('search_confirmation_button', 'n_clicks'),
    Input('advanced_search_button', 'n_clicks'),
    Input('multiple_product_dropdown', 'value'),
    
    State('type_search_product', 'value'),
    State('personnalized_sorting', 'data'),
    State('sliced_file', 'data'),
    State("dropdown_diet", "value"), 
    State('search_on', 'data'),
    State('dropdown_number_product', 'value'),
    State('shown_img', 'data'),
    State('history', 'data'),
    State('prevent_update', 'data'),
    State('input_search_adv', 'value'),
    State('language_user', 'data'),
    State('data_figure', 'data'),
    
    prevent_initial_call=True,
)

def display_images(*args):
    elapsed_time = time.time() if DEBUG else None
    
    # We unpack the args
    (pnns1_chosen, pnns2_chosen, country, search_bar, clicked_search, click_advanced_search, value_multiple_dropdown,
     type_search_product, selected_diet, df_slice, 
     dropdown_diet, search_on, n_best, shown_img_data, history_nav, prevent_update, user_input, language, data_figure) = args[-19:]
    
    # Return true if one of the diet was click.
    # It is helping for the browser history
    
    clicked_diet_ctx = [f'{diet}_div' for diet in diets]
    browser_diet = any(any(keyword in item['prop_id'] for keyword in clicked_diet_ctx) for item in ctx.triggered)
    
    # Initialize 
    no_display = {'display':'None'}
    images, styles_images, textes_images = [dash.no_update] * TOTAL_IMAGES, [no_display] * TOTAL_IMAGES, [None] * TOTAL_IMAGES
    style_top_graph_button, style_bottom_graph_button = no_display, no_display
    others_img, others_img_style = [None] * 4, [no_display] * 4
    subtitles, title = [None] * len(diets), None
    selected_product_img, selected_product_title, selected_product_texte = None, None, None
    graphic_gestion_style_bottom, graphic_gestion_style_top, selected_product_style, advanced_search_style = no_display, no_display, no_display, no_display
    search_on = False if search_on else dash.no_update
    selected_diet = None if selected_diet != None else dash.no_update
    style_multiple_dropdown = no_display
    style_picture_search_div = no_display
    browser_history_style = no_display
    
    # Setting some conditions
    condition_selected_a_product = ctx.triggered_id in ["search_bar", "multiple_product_dropdown"] + [f'{diet}_img_{i}' for diet in diets for i in range(20)]
    condition_selected_diet_search_navigation = (ctx.triggered_id in clicked_diet_ctx + ['search_confirmation_button']) or (browser_diet)
    
    # dataframe preparation, only when necessary
    if ctx.triggered_id not in ['advanced_search_button', 'search_confirmation_button']:
        df = return_df(country, pnns1_chosen, pnns2_chosen)
        
    elif ctx.triggered_id == 'search_confirmation_button':
        df = pd.read_json(StringIO(df_slice), orient='split', dtype={'code': str})
        # We adjust if the user has entered a value
        if user_input is not None:
            df = df.query('product_name.str.contains(@user_input)')
        
    # If clicking on diet preference or confirmed search or from the browser
    if (ctx.triggered_id in clicked_diet_ctx + ['search_confirmation_button']) or (browser_diet): 
        (subtitles, images, styles_images, 
        textes_images, prevent_update, search_on, history_nav, style_bottom_graph_button) = clicked_diet_navigation(translation, df, diets, n_best, 
                                        subtitles, images, styles_images, textes_images, language, search_on, history_nav, style_bottom_graph_button)
        
    # When navigating on the left panel    
    elif ctx.triggered_id in ['pnns1_chosen', 'pnns2_chosen', 'dropdown_country']:
        
        (title, subtitles, images, styles_images,
         textes_images, prevent_update) = pnns_country(translation, df, diets, n_best, subtitles, 
                                                        images, styles_images, textes_images, language)
                                
    # If the client clicked on the search bar or one of the picture
    elif condition_selected_a_product:
        
        try:
            # If searched by the search bar
            if ctx.triggered_id == "search_bar":
                # We check if it is a product name or code entered

                if type_search_product == "product_name":
                    product_code = get_data().query('product_name == @search_bar').get('code')
                    # If more than 1 product
                    if product_code.shape[0] > 1:
                        code = str(value_multiple_dropdown)
                        style_multiple_dropdown = {'display':'block'}
                    else:
                        code = product_code.values[0]

                elif type_search_product == "product_code":
                    code = str(search_bar)

            # If searched by the intra search bar (multiple products with the same name)
            elif ctx.triggered_id == "multiple_product_dropdown":
                # We get the code
                code = str(value_multiple_dropdown)
                style_multiple_dropdown = {'display':'block'}

            # If searched by clicking on image
            else: 
                url = shown_img_data[ctx.triggered_id]
                code = get_code(url)

            df_product = get_data().query('code == @code')

            # For now it helps to deal with the 0 problem.
            if df_product.shape[0] == 0:
                code = "0"*(13 - len(code)) + code
                df_product = get_data().query('code == @code')

            # We get the product's name
            product_name = df_product['product_name'].values[0]

            # Principale image
            selected_product_img = get_image(code)

            # Secondaries images
            # Return the link of the image, then check it's validity
            
            others_img = [get_image(code, i) for i in range(1, 5)]
            others_img = testing_img(others_img)
            

            # Display image if link correct
            others_img_style = [{'height': '150px', 'width': '150px'}
                               if others_img[i] != None else no_display
                               for i in range(0, 4)]

            selected_product_title = html.Strong(product_name)
            selected_product_texte = get_texte_product(df_product.iloc[0], language)

            pnns1 = df_product["pnns_groups_1"].values[0]
            pnns2 = df_product["pnns_groups_2"].values[0]

            # We add to the navigation history
            history_nav.insert(0, [f"Product: {product_name}", country, pnns1, pnns2, None, code])

            # If the product visualize is the same as before, we prevent some of the front end update
            if pnns2 == prevent_update:

                title = dash.no_update
                subtitles = [dash.no_update] * len(diets)
                styles_images = [dash.no_update] * TOTAL_IMAGES
                textes_images = [dash.no_update] * TOTAL_IMAGES

                prevent_update, pnns1_chosen, pnns2_chosen = ([dash.no_update]*3)

            else:
                df = return_df(country, pnns1, pnns2).copy()

                title = html.Strong(translations[language]['best_recommended_products'])

                subtitles, images, styles_images, textes_images = generate_texte_image(df, diets, n_best, 
                                                                                       subtitles, images, 
                                                                                       styles_images, textes_images,
                                                                                       language)
                # Checking each images
                images = testing_img(images)
                # Replace images
                images = [dash.get_asset_url('no_image.jpg') if url is None else url for url in images]
                
                prevent_update = pnns2
                pnns1_chosen, pnns2_chosen = pnns1, pnns2
            
        except:
            selected_product_img = dash.get_asset_url("no_image.jpg")
            selected_product_title = html.Strong(translations[language]['product_not_found'])
            selected_product_texte = html.Strong(translations[language]['product_not_available'])

            title = dash.no_update
            subtitles = [dash.no_update] * len(diets)
            styles_images = [dash.no_update] * TOTAL_IMAGES
            textes_images = [dash.no_update] * TOTAL_IMAGES
            prevent_update = None
        
        selected_product_style = {'display':'block'}
        style_top_graph_button = {'display':'block', 'color': 'black'}
        
    elif ctx.triggered_id == 'advanced_search_button':
        
        advanced_search_style = {'float': 'center', 'display': 'block', 'flex-direction': 'row', 
                                'width': '100%', 'background-color': '#F0F0F0', 'margin-bottom': '20px'}
        prevent_update = None
        
    # Top keep tract of the images src to load when clicking on 
    for i, src in enumerate(images):
        key = f'{diets[int(i/20)]}_img_{i%20}'
        if src == dash.no_update or src == None:
            continue
        else:
            shown_img_data[key] = src
            
    if condition_selected_a_product == False:
        pnns1_chosen = dash.no_update
        pnns2_chosen = dash.no_update
            
    output_values = [title, *subtitles, *images, *styles_images, *textes_images, *others_img, *others_img_style,
                     graphic_gestion_style_bottom, graphic_gestion_style_top, style_bottom_graph_button, style_top_graph_button, 
                     selected_diet, selected_product_style, 
                     selected_product_img, selected_product_title, selected_product_texte,
                     advanced_search_style, search_on, shown_img_data, history_nav, style_multiple_dropdown, 
                     browser_history_style, prevent_update, pnns1_chosen, pnns2_chosen, style_picture_search_div, data_figure]
    
    print("display_images: ", time.time() - elapsed_time) if DEBUG else None  
    return tuple(output_values)

    
def pnns_country(translation, df, diets, n_best, subtitles, images, styles_images, textes_images, language):

    # Modifying title
    title = html.Strong(translations[language]['best_recommended_products'])
    
    # Modifying subtitles, images and textes
    subtitles, images, styles_images, textes_images = generate_texte_image(df, diets, n_best, 
                                                                            subtitles, images, 
                                                                            styles_images, textes_images,
                                                                            language)
    
    # Checking each images
    images = testing_img(images)
    # Replace images
    images = [dash.get_asset_url('no_image.jpg') if url is None else url for url in images]
    
    prevent_update = pnns2_chosen if ctx.triggered_id == "pnns2_chosen" else None

    return title, subtitles, images, styles_images, textes_images, prevent_update

def clicked_diet_navigation(translation, df, diets, n_best, subtitles, images, styles_images, textes_images, language, search_on, history_nav, style_bottom_graph_button):

    for i, diet in enumerate([diet + "_div" for diet in diets]):
        subtitles[i] = html.Strong(f"{translations[language][diets[i]]}")
        
        if (ctx.triggered_id in ['search_confirmation_button', diet]) or browser_diet: 
            
            # If client clicked on the confirmation button of the advanced search
            if ctx.triggered_id == 'search_confirmation_button':
                # For the selected diet
                if diet[:-4] == dropdown_diet: #:-4 is to eliminate some text
                    selected_diet = diets[i] # To keep the selected button
                    advanced_search_style = dash.no_update
                    search_on = True
                    
                # If none selected
                elif (dropdown_diet == None) or (dropdown_diet == []):
                    selected_diet = "All"
                    advanced_search_style = dash.no_update
                    search_on = True
            
            # Elif client clicked on one of the diet button
            else:
                # We check which one is in ctx.triggered
                result = any(diet in item.get('prop_id', '') for item in ctx.triggered)
                
                # Add information when it is the selected diet
                if (diet == ctx.triggered_id) or (result):
                    selected_diet = diets[i] # To keep the selected button
                    
                    # We add to the navigation history
                    history_nav.insert(0, ["Navigation", country, pnns1_chosen, pnns2_chosen, diets[i], None])
            
            if selected_diet == diets[i]:
                
                title = html.Strong(f"BEST RECOMMENDED PRODUCTS FOR {diets[i].upper()}")

                # sort and retrieve the N best, then match the nutriscore image           
                df_N_best = df_sorting(diets[i], df).head(n_best)
                
                for y, (_, row) in enumerate(df_N_best.iterrows()):
                    index = y if i == 0 else (20 * i) + y

                    styles_images[index] = {'height': '400px', 'width': '400px'}
                    
                    # generate the texte below the image
                    textes_images[index] = get_texte_product(row, language)
                    
                    # We retrieve the image url via the code
                    images[index] = get_image(str(row.iloc[0]))
                    
                # Checking each images
                images = testing_img(images)
                # Replace images
                images = [dash.get_asset_url('no_image.jpg') if url is None else url for url in images]
                
                style_bottom_graph_button = {'display':'block', 'color': 'black'}
    
            # When the user doesn't specifie a diet to search on
            elif selected_diet == "All":
                subtitles, images, styles_images, textes_images = generate_texte_image(df, diets, n_best, 
                                                                            subtitles, images, 
                                                                            styles_images, textes_images,
                                                                            language)
                # Checking each images
                images = testing_img(images)
                # Replace images
                images = [dash.get_asset_url('no_image.jpg') if url is None else url for url in images]

    prevent_update = None

    return subtitles, images, styles_images, textes_images, prevent_update, search_on, history_nav, style_bottom_graph_button
