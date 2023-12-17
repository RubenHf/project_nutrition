import pickle
import tensorflow as tf
import os
import boto3

def load_model(model_save_path):
    model = tf.keras.models.load_model(model_save_path)
    return model

def load_preprocess(url):
    with open(url, "rb") as f:
        preprocess_input = pickle.load(f)
    return preprocess_input

# Function to load a file from S3
def download_file_from_s3(bucket_name, object_key, local_file_path):
    s3 = boto3.client('s3')

    try:
        s3.download_file(bucket_name, object_key, local_file_path)
    except Exception as e:
        print(f"Error downloading file: {str(e)}")

def remove_local_file(file_path):
    try:
        os.remove(file_path)
    except Exception as e:
        print(f"Error removing file: {str(e)}")

def load_API_models():
    # S3 bucket from the project and files
    bucket_name = 'nutritious.app'
    model1_file = 'developped_models/model_classification_pnns1_best_weights.h5'
    model2_file = 'developped_models/model_classification_pnns2_best_weights.h5'
    preprocess_file = 'developped_models/preprocess_input.pkl'

    # Local file paths to save the downloaded files
    local_model1_path = 'local_model1.h5'
    local_model2_path = 'local_model2.h5'
    local_preprocess_path = 'local_preprocess_input.pkl'

    # We download the files in the app directory
    download_file_from_s3(bucket_name, model1_file, local_model1_path)
    download_file_from_s3(bucket_name, model2_file, local_model2_path)
    download_file_from_s3(bucket_name, preprocess_file, local_preprocess_path)

    # We load the models and preprocess
    loaded_model_pnns1 = load_model(local_model1_path)
    loaded_model_pnns2 = load_model(local_model2_path)
    loaded_preprocess_input = load_preprocess(local_preprocess_path)

    # We remove the files from the app directory
    remove_local_file(local_model1_path)
    remove_local_file(local_model2_path)
    remove_local_file(local_preprocess_path)

    return loaded_model_pnns1, loaded_model_pnns2, loaded_preprocess_input