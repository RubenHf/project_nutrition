import pickle
import tensorflow as tf
import os
import gc
import logging
from functions.S3_function import download_file_from_s3

# Set up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load the model from the path
def load_model(url):
    if os.path.exists(url):
        return tf.keras.models.load_model(url)
    else:
        logger.warning(f"No file present at '{url}'")
        return None 

# Load preprocess from the path
def load_preprocess(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return pickle.load(f)
    else:
        logger.warning(f"No file present at '{path}'")
        return None 
    
# Function to remove the files downloaded
def remove_local_file(file_path):
    try:
        if os.path.exists(file_path):
            # Remove local object
            os.remove(file_path)
            logger.info(f"Removing file '{file_path}'")
        else: 
            logger.warning(f"No file present at '{file_path}'")
    except Exception as e:
        logger.error(f"Error removing file '{file_path}': {str(e)}")

def load_API_models(model_file, preprocess_file):

    # Local file paths to save the downloaded files
    local_model_path = 'local_model_front_back.h5'
    local_preprocess_path = 'local_preprocess_input.pkl'

    print("[INFO] Downloading files...")

    # We download the files in the app directory
    download_file_from_s3(model_file, local_model_path)
    download_file_from_s3(preprocess_file, local_preprocess_path)

    print("[INFO] Loading files...")

    # We load the models and preprocess
    loaded_model = load_model(local_model_path)
    loaded_preprocess_input = load_preprocess(local_preprocess_path)

    print("[INFO] Deleting files...")

    # We remove the files from the app directory
    remove_local_file(local_model_path)
    remove_local_file(local_preprocess_path)

    gc.collect()
    return loaded_model, loaded_preprocess_input
    