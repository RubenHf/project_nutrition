from main import app
import logging

# Set up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)  

files_treating_step_1 = {'data_file_S3' : 'files/cleaned_data_test.csv',#'files/cleaned_data.csv', 
                  'data_file_S3_post_clean_up' :'files/cleaned_data_post_urls.csv'}

files_treating_step_2 = {'data_file_S3' : 'files/cleaned_data_post_urls.csv', 
                  'data_file_S3_post_clean_up' :'files/cleaned_data_post_images.csv'}

logger.info("[LAUNCHED URLS TREATMENT OF FILE]")
logger.info("[cleaned_data.csv]")

response = app.post("/process-data-urls/", files_treating_step_1)

logger.info("[FINISHED TREATMENT...]")
logger.info("[FILED GENERATED: cleaned_data_post_urls.csv]\n\n")

logger.info("[LAUNCHED IMAGES TREATMENT OF FILE]")
logger.info("[cleaned_data_post_urls.csv]")

response = app.post("/process-data-image/", files_treating_step_2)

logger.info("[FINISHED TREATMENT...]")
logger.info("[FILED GENERATED: cleaned_data_post_images.csv]\n\n")