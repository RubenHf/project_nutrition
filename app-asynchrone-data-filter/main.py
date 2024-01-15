from fastapi import FastAPI, Form, BackgroundTasks
import pandas as pd
import gc
import logging
from functions.check_images import check_data_image
from functions.check_urls import testing_urls_data, generate_urls
from functions.path_functions import remove_local_file, create_pickle_file
from functions.s3_functions import upload_file_to_s3, load_csv_from_s3, load_pickle_from_s3


app = FastAPI()

# Set up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)  

@app.get("/")
def home():
    return {"health_check": "OK"}


async def process_urls(
    data_file_S3: str = Form(None),
    data_file_S3_post_urls_clean_up : str = Form(None)):

    # S3 bucket from the project and files
    bucket_name = 'nutritious.app'
    checked_images_S3 = 'files/checked_images.pkl'
    failed_images_S3 = 'files/failed_images.pkl'

    # Local file paths to save the downloaded files
    local_data_path = 'local_data.csv'
    local_checked_path = 'checked_images.pkl'
    local_failed_path = 'failed_images.pkl'

    print("[INFO] Loading files from S3...")

    df = load_csv_from_s3(bucket_name, data_file_S3, sep='\t')
    checked_images = load_pickle_from_s3(bucket_name, checked_images_S3)
    failed_images = load_pickle_from_s3(bucket_name, failed_images_S3)

    print("[INFO] Generating urls...")
    
    df = generate_urls(df)

    print("[INFO] Checking urls...")

    # Calling function to check urls in dataframe
    df = testing_urls_data(df, checked_images, failed_images)
    
    print("[INFO] Eliminating failed urls from data...")

    # Eliminating failed urls
    for images in ["image_1", "image_2", "image_3", "image_4"]:
        df[images] = df[images].apply(lambda x: None if x in failed_images else x)

    print("[INFO] Creating files in local...")

    # Create file in path
    df.to_csv(local_data_path, sep = "\t", index=None)
    create_pickle_file(checked_images, local_checked_path)
    create_pickle_file(failed_images, local_failed_path)

    print("[INFO] Uploading files to S3...")

    # We upload the new files
    upload_file_to_s3(local_data_path, bucket_name, data_file_S3_post_urls_clean_up)
    upload_file_to_s3(local_checked_path, bucket_name, checked_images_S3)
    upload_file_to_s3(local_failed_path, bucket_name, failed_images_S3)

    print("[INFO] Deleting files from local...")

    # We remove the files from the app directory
    remove_local_file(local_data_path)
    remove_local_file(local_checked_path)
    remove_local_file(local_failed_path)

    gc.collect()

async def process_images(
    data_file_S3: str = Form(None),
    data_file_S3_post_images_clean_up : str = Form(None)
    ):

    # S3 bucket from the project and files
    bucket_name = 'nutritious.app'

    # Local file paths to save the file
    local_data_path = 'local_data.csv'

    print("[INFO] Loading file from S3...")

    df = load_csv_from_s3(bucket_name, data_file_S3, sep='\t')

    print("[INFO] Checking images...")

    # Calling function to check images in dataframe
    df = check_data_image(df)

    # We clean the data
    df = df[df.image_1.notna()].copy()

    print("[INFO] Creating file in local...")

    # Create file in path
    df.to_csv(local_data_path, sep = "\t", index=None)

    print("[INFO] Uploading file to S3...")

    # We upload the new file
    upload_file_to_s3(local_data_path, bucket_name, data_file_S3_post_images_clean_up)

    print("[INFO] Deleting files in local...")

    # We remove the files from the app directory
    remove_local_file(local_data_path)

    gc.collect()

@app.post("/clean-up-data/")
async def process_image_endpoint(
    background_tasks: BackgroundTasks,
    data_file_S3: str = Form(None),
    data_file_S3_post_urls_clean_up : str = Form(None),
    data_file_S3_post_images_clean_up : str = Form(None)
    ):
    
    background_tasks.add_task(process_urls, data_file_S3, data_file_S3_post_urls_clean_up)
    background_tasks.add_task(process_images, data_file_S3_post_urls_clean_up, data_file_S3_post_images_clean_up)
    
    return {"message": "Operation launched in background"}

@app.post("/process-data-urls/")
async def process_urls_endpoint(
    background_tasks: BackgroundTasks,
    data_file_S3: str = Form(None),
    data_file_S3_post_urls_clean_up : str = Form(None)
    ):

    background_tasks.add_task(process_urls, data_file_S3, data_file_S3_post_urls_clean_up)

    return {"message": "Url processing operation launched in the background"}

@app.post("/process-data-image/")
async def process_image_endpoint(
    background_tasks: BackgroundTasks,
    data_file_S3: str = Form(None),
    data_file_S3_post_images_clean_up : str = Form(None)
    ):

    background_tasks.add_task(process_urls, data_file_S3, data_file_S3_post_images_clean_up)

    return {"message": "Url processing operation launched in the background"}