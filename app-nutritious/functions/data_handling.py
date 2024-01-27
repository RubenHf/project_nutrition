import pandas as pd
import copy
import os
from io import StringIO
import boto3
import logging
from dash import html, get_asset_url
from functions.language import get_translate

# Set up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)  

# Read environment variable from Heroku config vars
bucket_name = os.environ.get('S3_BUCKET_NAME')

if bucket_name is None:
    raise EnvironmentError("The 'S3_BUCKET_NAME' environment variable is not set.")

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
            
            images[index] = IMG["image_1"]

            styles_images[index] = {'width': '150px', 'height': '150px'}

            textes_images[index] = (
                html.Div([
                    get_nutriscore_image(str(IMG["nutriscore_score_letter"]))
                ] + [
                html.Div(IMG["product_name"], style={'text-align': 'center', 'margin-top': '5px'}) 
                ])
            ) 
    
    return subtitles, images, styles_images, textes_images   

# Return image of nutriscore
def get_nutriscore_image(img, style={'width': '100px', 'height': '50px', 'margin-left':'10px'}):
    return html.Img(
            src=get_asset_url(img),
                alt="Product Nutriscore",
                style=style
            )
    
    
# Return Image of nutriscore then the text below with nutrition informations
def get_texte_product(row, language):
    return html.Div([
        get_nutriscore_image(str(row["nutriscore_score_letter"]))
        ] + [
        html.Div([
            # Get the dictionnary, then get the translated word. If not in, get the initial value
            html.Strong(f"{translations.get(language, {}).get(row.index[i], row.index[i])}:"),
            f" {translations.get(language, {}).get(row.iloc[i], row.iloc[i])}"],
            style={'text-align': 'left', 'margin-top': '1px', 'margin-left':'10px', 'white-space': 'nowrap'}
            )
        for i in range(len(row.iloc[:-1]))
        if row.index[i] not in  [f"image_{i}" for i in range(1,5,1)] # To exclude images urls
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

# When debugging, it will load the file in local
# On server, it will load from S3
try:
    logger.info("Loading file from local folder...")
    # Get the directory of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Go up one level to the parent directory (assuming the script is in the 'app' directory)
    app_dir = os.path.dirname(script_dir)

    try:
        # Define the path to the file in the /files directory
        file_path = os.path.join(app_dir, 'files_dash', 'cleaned_img_data.csv')
    except:
        logger.info("status: Error")
        logger.info(f"message: {str(e)}")

    # Now you can use the file_path to access your file
    with open(file_path, 'r') as file:
        data = pd.read_csv(file_path, sep = "\t")
except:
    s3 = boto3.client('s3')

    # Path to the cleaned file
    data_file = 'files/cleaned_img_data.csv'

    try:
        logger.info("Loading file from S3 bucket...")
        # Read the CSV file from S3 into a Pandas DataFrame
        response = s3.get_object(Bucket=bucket_name, Key=data_file)
        content = response['Body'].read().decode('utf-8')
        data = pd.read_csv(StringIO(content), sep='\t')

    except Exception as e:
        logger.info("status: Error downloading file")
        logger.info(f"message: {str(e)}")

# We do the mapping of nutriscore
data = mapping_nutriscore_IMG(data)


