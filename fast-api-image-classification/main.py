from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import List
from io import BytesIO
import base64
from functions.loading_api import load_API_models
from functions.others_functions import get_model_input_size
from functions.images_functions import process_image, img_prediction_model_pnns
import gc
import logging

# We import the initials values for loading models and preprocesses
from config import *

# Set up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# We load the models and the preprocesses
loaded_model_front, loaded_preprocess_input_front = load_API_models(S3_path_model_front, S3_path_preprocess_front)
target_size_front = get_model_input_size(loaded_model_front)
loaded_model_pnns1, loaded_preprocess_input_pnns = load_API_models(S3_path_model_pnns1, S3_path_preprocess_pnns)
target_size_pnns = get_model_input_size(loaded_model_pnns1)
loaded_model_pnns2, _ = load_API_models(S3_path_model_pnns2, S3_path_preprocess_pnns)

@app.get("/")
def home():
    return {"health_check": "OK"}

@app.post("/front-process-image/")
async def process_image_endpoint(file: UploadFile = File(...)):
    try:
        logger.info(f"Processing unique image")
        # Uploaded file as to be one of those extension
        if file.content_type not in ["image/png", "image/jpeg", "image/jpg"]:
            raise ValueError("Only PNG, JPEG or JPG images are allowed.")

        # Read the file content
        file_contents = await file.read()

        # Process the image
        try:
            result = process_image(BytesIO(file_contents), loaded_model_front, loaded_preprocess_input_front, target_size_front)
            
        except Exception as e:
            logger.warning("status: error processing image")
            logger.warning(f"message: {str(e)}")
            result = "None"

        gc.collect()

        return JSONResponse(content=result)
    except Exception as e:
        logger.warning("status: error processing single image")
        logger.warning(f"message: {str(e)}")
        return  "None"
    
@app.post("/front-process-batch-images/")
async def process_batch_images_endpoint(files: List[UploadFile] = File(...)):
    try:
        logger.info(f"Processing image in batch")
        # Check if files list is empty
        if not files:
            raise ValueError("No files provided.")

        # Process each image in the batch
        results = []
        for file in files:
            if file.content_type not in ["image/png", "image/jpeg", "image/jpg"]:
                raise ValueError(f"Only PNG, JPEG, or JPG images are allowed. File: {file.filename}")

            # Read the file content
            file_contents = await file.read()

            # Process the image
            try:
                result = process_image(BytesIO(file_contents), loaded_model_front, loaded_preprocess_input_front, target_size_front)

            except Exception as e:
                logger.warning("status: error processing image in batch")
                logger.warning(f"message: {str(e)}")
                result = "None"

            results.append(result)
        
        # Clear memory (optional)
        gc.collect()

        return JSONResponse(content=results)
    except Exception as e:
        logger.warning("status: error during processing batch")
        logger.warning(f"message: {str(e)}")
        return  ["None"] * len(files)

@app.post("/pnns-process-image/")
async def process_image_endpoint(
    file: UploadFile = File(None), 
    base64_image: str = Form(None), 
    pnns_groups: str = Form(None)):
        
    logger.info("API was called...")

    try:
        if file:
        # If file image is provided, decode it
            
            logger.info("A file was uploaded")

            # Uploaded file as to be one of those extension
            if file.content_type not in ["image/png", "image/jpeg", "image/jpg"]:
                raise ValueError("Only PNG, JPEG or JPG images are allowed.")

            # Read the file content
            file_contents = await file.read()


        elif base64_image:
        # If base64 image is provided, we decode it
            
            logger.info("A base64 image was uploaded")

            if 'base64,' in base64_image:
                data_split = base64_image.split('base64,')
            
                encoded_data = data_split[1]
            
                file_contents = base64.b64decode(encoded_data)

            else: 
                file_contents = base64.b64decode(base64_image)

        # We do the prediction on 
            
        logger.info(f"The prediction is done on {pnns_groups}")
        
        if pnns_groups == "pnns_groups_2":
            result = img_prediction_model_pnns(BytesIO(file_contents), pnns_groups, loaded_model_pnns2, loaded_preprocess_input_pnns, target_size_pnns)
        else:
            # Default condition, if pnns_groups == None or pnns_groups_1
            pnns_groups = "pnns_groups_1"
            result = img_prediction_model_pnns(BytesIO(file_contents), pnns_groups, loaded_model_pnns1, loaded_preprocess_input_pnns, target_size_pnns)
        gc.collect()
        
        logger.info("...successful prediction")

        return JSONResponse(content=result)

    except Exception as e:
        
        logger.info("status: error")
        logger.info(f"message: {str(e)}")

        return JSONResponse(content={"status": "error", "message": str(e)})
