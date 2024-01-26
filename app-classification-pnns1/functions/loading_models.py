import pickle
import tensorflow as tf
import os
import boto3
import gc

# Read environment variable from Heroku config vars
bucket_name = os.environ.get('S3_BUCKET_NAME')

if bucket_name is None:
    raise EnvironmentError("The 'S3_BUCKET_NAME' environment variable is not set.")

# Load the model from the path
def load_model(path):
    if os.path.exists(path):
        return tf.keras.models.load_model(path)
    else:
        print(f"Error: File '{path}' not found.")
        return None 

# Load preprocess from the path
def load_preprocess(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return pickle.load(f)
    else:
        print(f"Error: File '{path}' not found.")
        return None 

# Function to load a file from S3
def download_file_from_s3(bucket_name, object_key, local_file_path):
    s3 = boto3.client('s3')

    try:
        # Download object in local from bucket
        s3.download_file(bucket_name, object_key, local_file_path)
    except Exception as e:
        print(f"Error downloading file: {str(e)}")

# Function to remove the files downloaded
def remove_local_file(file_path):
    try:
        if os.path.exists(file_path):
            # Remove local object
            os.remove(file_path)
        else: 
            print("No file present")
    except Exception as e:
        print(f"Error removing file: {str(e)}")

def load_API_models():
    # S3 bucket from the project and files
    model1_file = 'developped_models/model_classification_pnns1_best_weights.h5'
    model2_file = 'developped_models/model_classification_pnns2_best_weights.h5'
    preprocess_file = 'developped_models/preprocess_input.pkl'

    # Local file paths to save the downloaded files
    local_model1_path = 'local_model1.h5'
    local_model2_path = 'local_model2.h5'
    local_preprocess_path = 'local_preprocess_input.pkl'


    print("Downloading files...")

    # We download the files in the app directory
    download_file_from_s3(bucket_name, model1_file, local_model1_path)
    download_file_from_s3(bucket_name, model2_file, local_model2_path)
    download_file_from_s3(bucket_name, preprocess_file, local_preprocess_path)

    print("Loading files...")

    # We load the models and preprocess
    loaded_model_pnns1 = load_model(local_model1_path)
    loaded_model_pnns2 = load_model(local_model2_path)
    loaded_preprocess_input = load_preprocess(local_preprocess_path)

    print("Deleting files...")

    # We remove the files from the app directory
    remove_local_file(local_model1_path)
    remove_local_file(local_model2_path)
    remove_local_file(local_preprocess_path)

    gc.collect()
    return loaded_model_pnns1, loaded_model_pnns2, loaded_preprocess_input