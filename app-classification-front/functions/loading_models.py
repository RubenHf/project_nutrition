import pickle
import tensorflow as tf
import os
import boto3
import gc
import logging

# Set up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Read environment variable from Heroku config vars
bucket_name = os.environ.get('S3_BUCKET_NAME')

if bucket_name is None:
    raise EnvironmentError("The 'S3_BUCKET_NAME' environment variable is not set.")


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
    
# Get the input shape of the model
def get_model_input_size(model):
    input_shape = model.layers[0].input_shape[0][1:3]

    logger.info(f"Input shape of model: {input_shape}")
    
    return input_shape

# Function to load a file from S3
def download_file_from_s3(bucket_name, object_key, local_file_path):
    s3 = boto3.client('s3')

    try:
        # Download object in local from bucket
        s3.download_file(bucket_name, object_key, local_file_path)
        logger.info(f"Downloaded file '{object_key}' to '{local_file_path}'")
    
    except Exception as e:
        logger.error(f"Error downloading file '{object_key}': {str(e)}")

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

def load_API_models():
    # We load the files from the S3 bucket
    model1_file = 'developped_models/model_classification_front_back_mobilevnet2.h5'
    preprocess_file = 'developped_models/preprocess_input_mobilevnet2.pkl'

    # Local file paths to save the downloaded files
    local_model_path = 'local_model_front_back.h5'
    local_preprocess_path = 'local_preprocess_input.pkl'

    print("[INFO] Downloading files...")

    # We download the files in the app directory
    download_file_from_s3(bucket_name, model1_file, local_model_path)
    download_file_from_s3(bucket_name, preprocess_file, local_preprocess_path)

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
    