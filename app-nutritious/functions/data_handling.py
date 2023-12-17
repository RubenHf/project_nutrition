import pandas as pd
import copy
import os
import dash
from dash import html
import requests
import concurrent.futures
import queue
from functions.language import get_translate

# We retrieve the language dictionnary
translations = get_translate()

# Return the pd.DataFrame
def get_data():
    return data

# Return a list with the name of the countries in the dataset
def get_unique_countries():
    # Options setup for dropdown of countries
    c1 = [country.split(",") for country in data.countries_en.unique()]
    c2 = [count for country in c1 for count in country]
    unique_countries = sorted(list(set(c2)))

    return unique_countries

# Return a list of dicts with the number of products by country
def products_by_countries(language):

    flags = {"United States":"\U0001F1FA\U0001F1F8", 
             "France":"\U0001F1EB\U0001F1F7", 
             "Germany":"\U0001F1E9\U0001F1EA", 
             "United Kingdom":"\U0001F1EC\U0001F1E7"}
    
    nb_products_countries = [
        {
            'label': f"{flags[country]} {translations[language][country]} [{return_df(country).shape[0]} products]",
            'value': country
        } 
        for country in get_unique_countries()
    ]

    return nb_products_countries

# Return a list of the pnns_groups 1 and sorted
def get_pnns_groups_1():
    return sorted(data.pnns_groups_1.unique())

# Return a list of the pnns_groups 2 and sorted
def get_pnns_groups_2():

    pnns_groups_2 = []
    for pnns1 in get_pnns_groups_1():
        for pnns2 in sorted(data.loc[data.pnns_groups_1 == pnns1, 'pnns_groups_2'].unique()):
            if pnns2 not in ['unknown', 'Alcoholic beverages']:
                pnns_groups_2.append(pnns2)

    return pnns_groups_2


def get_pnns_groups():

    pnns_groups = {}
    for pnns1 in get_pnns_groups_1():
        pnns_groups[pnns1] = sorted(data.loc[data.pnns_groups_1 == pnns1, "pnns_groups_2"].unique().tolist())

    return pnns_groups


def pnns_groups_options(country, pnns_groups_num, language, pnns1=None):
    if pnns_groups_num == "pnns_groups_1":
        pnns_groups = data[pnns_groups_num].unique()
    elif pnns_groups_num == "pnns_groups_2":
        pnns_groups = data.loc[data.pnns_groups_1 == pnns1, pnns_groups_num].unique()

    # Create a DataFrame with counts for each pnns group
    counts_df = data.query('countries_en.str.contains(@country)').groupby(pnns_groups_num).size().reset_index(name='count')

    # Merge the counts with the unique pnns groups
    merged_df = pd.DataFrame({pnns_groups_num: pnns_groups})
    merged_df = pd.merge(merged_df, counts_df, on=pnns_groups_num, how='left').fillna(0)
    
    merged_df.sort_values(by=pnns_groups_num, inplace=True)
    
    # Create the pnns_groups_options list
    pnns_groups_options = [
        {
            'label': f"{translations[language][pnns]} [{count} products]",
            'value': pnns
        }
        for pnns, count in zip(merged_df[pnns_groups_num], merged_df['count'])
    ]

    return pnns_groups_options  

def cache(fun):
    cache.cache_ = {}

    def inner(country, pnns1, pnns2):
        # Check if the inputs have changed
        inputs_changed = (
            country not in cache.cache_ or
            pnns1 not in cache.cache_ or
            pnns2 not in cache.cache_
        )
        
        cache_key = (country, pnns1, pnns2)

        if inputs_changed or cache_key not in cache.cache_:
            cache.cache_[cache_key] = fun(country, pnns1, pnns2)

        return cache.cache_[cache_key]

    return inner

@cache
def function(country, pnns1, pnns2):
    
    df = data.query('countries_en.str.contains(@country)')
    
    if pnns2:
        df = df.query('pnns_groups_2 == @pnns2')
    elif pnns1:
        df = df.query('pnns_groups_1 == @pnns1')

    return df

def return_df(country, pnns1 = None, pnns2 = None):

    if country:
        return function(country, pnns1, pnns2)

    # Returning no data to show
    else:
        return None

def get_image(code, number = 1):
    # Transform the code to produce the Open Food Facts image URL
    # number = the image we choose to retrieve
    if len(code) <= 8:
        url = f'https://images.openfoodfacts.org/images/products/{code}/{number}.jpg'
        return url
    elif len(code) > 8:
        code = "0"*(13 - len(code)) + code
        url = f'https://images.openfoodfacts.org/images/products/{code[:3]}/{code[3:6]}/{code[6:9]}/{code[9:]}/{number}.jpg'
        return url
    else:
        return None

def check_url_image(url):
    """
    Check if the link of the image is correct
    Return none if not
    """
    
    try:
        response = requests.head(url) # We use head instead of get, we only need to check the link
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        return url
    except requests.exceptions.RequestException:
        return None

def check_image_urls_parallel(urls):
    """
    The check_image_urls_parallel function uses concurrent.futures.ThreadPoolExecutor 
    to perform the checks concurrently.
    """
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        #The map function is used to apply the check_url function to each URL in parallel.
        results = executor.map(check_url_image, urls) # return a generator
        
    #The check_url_image function puts the results appropriate queue (checked_queue or failed_queue)
    for result in results:
        if result is not None:
            checked_queue.put(result)
        else:
            failed_queue.put(result)   
        
# Store globally informations on the url images.
# If one user check one image, it will be beneficial to all
# failed_img contains the url that failed.
checked_images = set()
failed_img = set()

# We set a queue for allowing a multi user environment 
checked_queue = queue.Queue()
failed_queue = queue.Queue()

def testing_img(images):
    to_test = []

    for i, url in enumerate(images):
        if url in checked_images:
            if url in failed_img:
                images[i] = None
        else: 
            if url is not None and 'http' in str(url): 
                checked_images.add(url)
                to_test.append(url)

    check_image_urls_parallel(to_test)
    
    # The queue helps us handle a multi users environement
    while not checked_queue.empty():
        url = checked_queue.get()
        checked_images.add(url)

    while not failed_queue.empty():
        url = failed_queue.get()
        failed_img.add(url)

    for i, url in enumerate(images):
        if url in failed_img:
            images[i] = None
      
    return images
        
        
def get_code(url):
    # Extract the product code from the Open Food Facts image URL
    try:
        parts = url.split('/')
        
        # Short code format
        if parts[-3] == 'products':
            return parts[-2]
        
        # Long code format
        else:
            code = parts[-5] + parts[-4] + parts[-3] + parts[-2]
            return code.lstrip('0')  # Remove leading zeros
    except:
        pass

    return None

def mapping_nutriscore_IMG(df):
    """
        Function matching the nutriscore to the letter A to E
        Add the column nutriscore_score_letter to the dataframe
        We loop inside the dictionnary, and change the letter if the score is inferior.
        Until it isn't
    """
    nutriscore_img = {
        "E" : ["40", "nutriscore_E.png"], 
        "D" : ["18", "nutriscore_D.png"],
        "C" : ["10", "nutriscore_C.png"],
        "B" : ["2", "nutriscore_B.png"],
        "A" : ["-1", "nutriscore_A.png"],
    }
    if isinstance(df, pd.DataFrame):   
        df["nutriscore_score_letter"] = "nutriscore_E.png"
        for letter in nutriscore_img:
            df.loc[: ,"nutriscore_score_letter"] = df.apply(lambda x: nutriscore_img[letter][1] 
                                                if x["nutriscore_score"] <= int(nutriscore_img[letter][0])
                                               else x["nutriscore_score_letter"], axis = 1)
        return df

def df_sorting(diet, df = None):
    """
        Function sorting the dataframe
        ascending = True
        Descending = False
    """

    type_diet = {
        "Healthier foods": [
            {'column_id': 'nutriscore_score', 'direction': True},
        ],
        "Fiber rich foods": [
            {'column_id': 'fiber_100g', 'direction': False},
            {'column_id': 'nutriscore_score', 'direction': True}
        ],
        "Low sugar foods": [
            {'column_id': 'carbohydrates_100g', 'direction': True},
            {'column_id': 'nutriscore_score', 'direction': True}
        ],
        "Protein rich foods": [
            {'column_id': 'proteins_100g', 'direction': False},
            {'column_id': 'nutriscore_score', 'direction': True}
        ],
        "Energy rich foods": [
            {'column_id': 'energy_100g', 'direction': False},
            {'column_id': 'nutriscore_score', 'direction': True}
        ],
        "Low fat foods": [
            {'column_id': 'fat_100g', 'direction': True},
            {'column_id': 'nutriscore_score', 'direction': True}
        ],
        "Low salt foods": [
            {'column_id': 'salt_100g', 'direction': True},
            {'column_id': 'nutriscore_score', 'direction': True}
        ],
        "Low saturated fat foods": [
            {'column_id': 'saturated-fat_100g', 'direction': True},
            {'column_id': 'nutriscore_score', 'direction': True}
        ],
    }
    column_id = []
    direction = []
    
    df_copy = copy.deepcopy(df)
    
    if diet in type_diet:
        for sorting_param in type_diet[diet]:
            
            column_id.append(sorting_param['column_id'])
            direction.append(sorting_param['direction'])
            
        if isinstance(df, pd.DataFrame):  
            df_copy = df_copy.sort_values(by=column_id, ascending=direction)
    
    if isinstance(df_copy, pd.DataFrame):
        return df_copy
    else: 
        return column_id

    
# Function filling the list subtitles, images, styles_images, textes_images
def generate_texte_image(df, diets, n_best, subtitles, images, styles_images, textes_images, language):                 
    for i, diet in enumerate(diets):
        subtitles[i] = html.Strong(f"{translations[language][diet]}")
        
        # We sort, we take the n_best then we map the nutriscore label
        df_N_best = df_sorting(diet, df).head(n_best)

        for y, (_, IMG) in enumerate(df_N_best.iterrows()):
            index = y if i == 0 else (20 * i) + y
            code = IMG.iloc[0]
            product_name = IMG.iloc[1]
            
            # We retrieve the image url via the code
            images[index] = get_image(str(code))

            styles_images[index] = {'width': '150px', 'height': '150px'}

            textes_images[index] = (
                html.Div([
                    get_nutriscore_image(str(IMG.iloc[-1]))
                ] + [
                html.Div(product_name, style={'text-align': 'center', 'margin-top': '5px'}) 
                ])
            ) 
    # Checking each images
    #images = check_image_urls_parallel(images)
    images = testing_img(images)
    # Replace image 
    images = [dash.get_asset_url('no_image.jpg') if url is None else url for url in images]
    
    return subtitles, images, styles_images, textes_images   

# Return image of nutriscore
def get_nutriscore_image(img, style={'width': '100px', 'height': '50px', 'margin-left':'10px'}):
    return html.Img(
            src=dash.get_asset_url(img),
                alt="Product Nutriscore",
                style=style
            )
    
    
# Return Image of nutriscore then the text below with nutrition informations
def get_texte_product(row, language):
    return html.Div([
        get_nutriscore_image(str(row.iloc[-1]))
        ] + [
        html.Div([
            # Get the dictionnary, then get the translated word. If not in, get the initial value
            html.Strong(f"{translations.get(language, {}).get(row.index[i], row.index[i])}:"),
            f" {translations.get(language, {}).get(row.iloc[i], row.iloc[i])}"],
            style={'text-align': 'left', 'margin-top': '1px', 'margin-left':'10px', 'white-space': 'nowrap'}
            )
        for i in range(len(row.iloc[:-1]))
    ], style={'display': 'flex', 'flex-direction': 'column', 'overflowX': 'scroll'})
    
def find_key_by_value(my_dict, value):
    """
    Function searching which key contains the value
    Args: The dict to search in and the value to search
    Return None, if not in the dict
    
    """
    
    for key, val in my_dict.items():
        if value in val:
            return key
    # If the value is not found
    return None 

try:
    # Define the path to the file in the /files directory
    file_path='cleaned_data.csv'
    # Now you can use the file_path to access your file
    with open(file_path, 'r') as file:
        data = pd.read_csv(file_path, sep = "\t")

except:
    # Get the directory of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Go up one level to the parent directory (assuming the script is in the 'app' directory)
    app_dir = os.path.dirname(script_dir)

    # Define the path to the file in the /files directory
    file_path = os.path.join(app_dir, 'files_dash', 'cleaned_data.csv')

    # Now you can use the file_path to access your file
    with open(file_path, 'r') as file:
        data = pd.read_csv(file_path, sep = "\t")

# We do the mapping of nutriscore
data = mapping_nutriscore_IMG(data)