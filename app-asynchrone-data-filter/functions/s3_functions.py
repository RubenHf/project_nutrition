import boto3
import logging
import io
import pandas as pd
import pickle

# Set up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)  

# Function to load a file from S3
def download_file_from_s3(bucket_name, object_key, local_file_path):
    s3 = boto3.client('s3')

    try:
        # Download object in local from bucket
        s3.download_file(bucket_name, object_key, local_file_path)
        logger.info(f"Downloaded file '{object_key}' to '{local_file_path}'")
    
    except Exception as e:
        logger.error(f"Error downloading file '{object_key}': {str(e)}")

# Function to upload a file to S3
def upload_file_to_s3(local_file_path, bucket_name, object_key):
    s3 = boto3.client('s3')

    try:
        # Download object in local from bucket
        s3.upload_file(local_file_path, bucket_name, object_key)
        logger.info(f"Uploading file '{local_file_path}' to '{object_key}'")
    
    except FileNotFoundError:
        logger.error(f"File not found: '{local_file_path}'")

    except Exception as e:
        logger.error(f"Error uploading file '{object_key}': {str(e)}")

# Function to load a csv from s3 
def load_csv_from_s3(bucket_name, object_key, sep=','):
    s3 = boto3.client('s3')

    try:
        response = s3.get_object(Bucket=bucket_name, Key=object_key)
        return pd.read_csv(io.BytesIO(response['Body'].read()), sep=sep)
    
    except Exception as e:
        logger.error(f"Error uploading csv file '{object_key}': {str(e)}")
        return None

# Function to load a pickle from s3
def load_pickle_from_s3(bucket_name, object_key):
    s3 = boto3.client('s3')

    try:
        response = s3.get_object(Bucket=bucket_name, Key=object_key)
        return pickle.loads(response['Body'].read())
    
    except Exception as e:
        logger.error(f"Error uploading csv file '{object_key}': {str(e)}")
        return None