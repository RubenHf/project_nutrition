from functions.data_handling import get_data, products_by_countries,get_pnns_groups_1, get_pnns_groups_2, get_pnns_groups
from functions.language import get_translate, get_languages_options
import os

# We set the initials config

# Set default language
initial_language = 'en'

# Retrieve language dictionary
translations = get_translate()

option_languages = get_languages_options(translations[initial_language])

products_availability = str(get_data().shape[0])

nutrients = ["fat_100g", "saturated-fat_100g", "carbohydrates_100g", "fiber_100g", "proteins_100g", "salt_100g", "macronutrients_100g"]

slider_trigger = ["slider_energy", "slider_fat", "slider_saturated", "slider_carbohydrates", "slider_fiber", "slider_proteins", "slider_salt", "slider_macronutrients"]

diets = ["Healthier foods", "Fiber rich foods", "Low sugar foods", "Protein rich foods", "Low fat foods", "Low salt foods", "Low saturated fat foods", "Energy rich foods"]

# Default setup
default_diet = "Healthier foods" 

# Generate list of unique countries and number of products
unique_countries = products_by_countries(initial_language)

# Generate pnns_groups 1 and 2, and sorted
pnns_groups_1 = get_pnns_groups_1()

pnns_groups_2 = get_pnns_groups_2()

pnns_groups = get_pnns_groups()
  
# to handle increased number of diet
TOTAL_IMAGES = len(diets) * 20

# Read environment variable from config vars
api_classification_url = os.environ.get('API_CLASSIFICATION_URL')

if api_classification_url is None:
    raise EnvironmentError("The 'API_CLASSIFICATION_URL' environment variable is not set.")


