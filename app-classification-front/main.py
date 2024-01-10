from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from typing import List
from PIL import Image
from io import BytesIO
import tensorflow as tf
from functions.loading_models import load_API_models, get_model_input_size
import gc
import logging

# Set up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# We load the model and the preprocess
loaded_model, loaded_preprocess_input = load_API_models()
target_size = get_model_input_size(loaded_model)

def load_and_preprocess_image(image_path):
    # Load and preprocess a single image
    with tf.keras.preprocessing.image.load_img(image_path, target_size=target_size) as img:
        img_array = tf.keras.preprocessing.image.img_to_array(img)
        img_array = tf.expand_dims(img_array, 0)  # Create batch dimension
        
        # We use the loaded preprocess
        return loaded_preprocess_input(img_array)

def predict_on_image(image_path):
    preprocessed_image = load_and_preprocess_image(image_path)
    
    gc.collect()
    return loaded_model(preprocessed_image)

# Alternative to numpy.argmax 
def argmax(result):
    if len(result) == 1: # When list is nested
        return max(range(len(result[0])), key=result[0].__getitem__)
    else: 
        return max(range(len(result)), key=result.__getitem__)

def process_image(image_content):
    # Predict on the image

    result_prediction = str(argmax(predict_on_image(image_content)))

    gc.collect()
    
    # Return a dictionary or any other data you want
    return {"status": "success", "result": result_prediction}


@app.get("/")
def home():
    return {"health_check": "OK"}

@app.post("/process-image/")
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
            result = process_image(BytesIO(file_contents))
            
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
    
@app.post("/process-batch-images/")
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
                result = process_image(BytesIO(file_contents))

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
