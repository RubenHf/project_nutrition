import os
import boto3
import logging

# Set up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Read environment variable from config vars
bucket_name = os.environ.get('S3_BUCKET_NAME')
bucket_name = "nutritious.app"
if bucket_name is None:
    raise EnvironmentError("The 'S3_BUCKET_NAME' environment variable is not set.")

# Function to load a file from S3
def download_file_from_s3(object_key, local_file_path):
    s3 = boto3.client('s3')

    try:
        # Download object in local folder from bucket
        s3.download_file(bucket_name, object_key, local_file_path)
        logger.info(f"Downloaded file '{object_key}' to '{local_file_path}'")
    
    except Exception as e:
        # Signal if error
        logger.error(f"Error downloading file '{object_key}': {str(e)}")