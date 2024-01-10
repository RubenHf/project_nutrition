from fastapi import FastAPI
import pandas as pd
import gc
import logging
from functions.check_images import check_data_image
from functions.check_urls import testing_urls_data
from functions.path_functions import remove_local_file, load_pickle_file, create_pickle_file
from functions.s3_functions import download_file_from_s3, upload_file_to_s3


app = FastAPI()

# Set up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)  

@app.get("/")
def home():
    return {"health_check": "OK"}


@app.post("/process-data-urls/")
async def process_urls_endpoint():
    # S3 bucket from the project and files
    bucket_name = 'nutritious.app'
    data_file_S3 = 'files/cleaned_data_test.csv'
    checked_images_S3 = 'files/checked_images.pkl'
    failed_images_S3 = 'files/failed_images.pkl'

    # Local file paths to save the downloaded files
    local_data_path = 'local_data.csv'
    local_checked_path = 'checked_images.pkl'
    local_failed_path = 'failed_images.pkl'

    print("[INFO] Downloading files...")

    # We download the files in the app directory
    download_file_from_s3(bucket_name, data_file_S3, local_data_path)
    download_file_from_s3(bucket_name, checked_images_S3, local_checked_path)
    download_file_from_s3(bucket_name, failed_images_S3, local_failed_path)

    print("[INFO] Loading files...")

    df = pd.read_csv(local_data_path, sep = "\t")
    checked_images = load_pickle_file(local_checked_path)
    failed_images = load_pickle_file(local_failed_path)

    print("[INFO] Checking urls...")

    # Calling function to check urls in dataframe
    df = testing_urls_data(df, checked_images, failed_images)
    
    print("[INFO] Eliminating failed urls...")

    # Eliminating failed urls
    for images in ["image_1", "image_2", "image_3", "image_4"]:
        df[images] = df[images].apply(lambda x: None if x in failed_images else x)

    print("[INFO] Creating files...")

    # Create file in path
    df.to_csv(local_data_path, sep = "\t", index=None)
    create_pickle_file(checked_images, local_checked_path)
    create_pickle_file(failed_images, local_failed_path)

    print("[INFO] Uploading files...")

    # We upload the new files
    data_file_S3 = 'files/cleaned_image_data_test.csv' # For testing
    upload_file_to_s3(local_data_path, bucket_name, data_file_S3)
    upload_file_to_s3(local_checked_path, bucket_name, checked_images_S3)
    upload_file_to_s3(local_failed_path, bucket_name, failed_images_S3)

    print("[INFO] Deleting files...")

    # We remove the files from the app directory
    remove_local_file(local_data_path)
    remove_local_file(local_checked_path)
    remove_local_file(local_failed_path)

    gc.collect()

@app.post("/process-data-image/")
async def process_image_endpoint():
    # S3 bucket from the project and files
    bucket_name = 'nutritious.app'
    data_file_S3 = 'files/cleaned_image_data_test.csv'

    # Local file paths to save the downloaded files
    local_data_path = 'local_data.csv'

    print("[INFO] Downloading file...")

    # We download the files in the app directory
    download_file_from_s3(bucket_name, data_file_S3, local_data_path)

    print("[INFO] Loading file...")
    df = pd.read_csv(local_data_path, sep = "\t")

    print("[INFO] Checking images...")

    # Calling function to check images in dataframe
    df = check_data_image(df)
    # We clean the data
    df = df[df.image_1.notna()].copy()

    print("[INFO] Creating file...")

    # Create file in path
    df.to_csv(local_data_path, sep = "\t", index=None)

    print("[INFO] Uploading file...")

    data_file_S3 = 'files/cleaned_image_data_test_end.csv'
    # We upload the new file
    upload_file_to_s3(local_data_path, bucket_name, data_file_S3)

    print("[INFO] Deleting files...")
    # We remove the files from the app directory
    remove_local_file(local_data_path)

    gc.collect()