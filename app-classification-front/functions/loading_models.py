import pickle
import tensorflow as tf
import os
import boto3

# Load the model from the path
def load_model(model_save_path):
    if os.path.exists(model_save_path):
        model = tf.keras.models.load_model(model_save_path)
        return model
    else:
        print(f"Error: File '{url}' not found.")
        return None 

# Load preprocess
def load_preprocess(url):
    if os.path.exists(url):
        with open(url, "rb") as f:
            preprocess_input = pickle.load(f)
        return preprocess_input
    else:
        print(f"Error: File '{url}' not found.")
        return None 

# Function to load a file from S3
def download_file_from_s3(bucket_name, object_key, local_file_path):
    s3 = boto3.client('s3')

    try:
        # Download object in local from bucket
        s3.download_file(bucket_name, object_key, local_file_path)
    except Exception as e:
        print(f"Error downloading file: {str(e)}")

def remove_local_file(file_path):
    try:
        # Remove local object
        os.remove(file_path)
    except Exception as e:
        print(f"Error removing file: {str(e)}")

def load_API_models():
    # S3 bucket from the project and files
    bucket_name = 'nutritious.app'
    model1_file = 'developped_models/model_classification_front_back_best_weights.h5'
    preprocess_file = 'developped_models/preprocess_input.pkl'

    # Local file paths to save the downloaded files
    local_model_path = 'local_model_front_back.h5'
    local_preprocess_path = 'local_preprocess_input.pkl'

    print("Downloading files...")

    # We download the files in the app directory
    download_file_from_s3(bucket_name, model1_file, local_model_path)
    download_file_from_s3(bucket_name, preprocess_file, local_preprocess_path)

    print("Loading files...")

    # We load the models and preprocess
    loaded_model = load_model(local_model_path)
    loaded_preprocess_input = load_preprocess(local_preprocess_path)

    print("Deleting files...")

    # We remove the files from the app directory
    remove_local_file(local_model_path)
    remove_local_file(local_preprocess_path)

    return loaded_model, loaded_preprocess_input
    