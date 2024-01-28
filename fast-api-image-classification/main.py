from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import List
from PIL import Image
from io import BytesIO
import base64
import tensorflow as tf
from functions.loading_api import load_API_models
from functions.others_functions import get_model_input_size
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

def load_and_preprocess_image(image_path, preprocess_input, target_size):
    # Load and preprocess a single image
    with tf.keras.preprocessing.image.load_img(image_path, target_size=target_size) as img:
        img_array = tf.keras.preprocessing.image.img_to_array(img)
        img_array = tf.expand_dims(img_array, 0)  # Create batch dimension
        
        # We return the image after preprocessing
        return preprocess_input(img_array)

def predict_on_image(image_path, model, preprocess_input, target_size):
    preprocessed_image = load_and_preprocess_image(image_path, preprocess_input, target_size)
    
    try:
        predictions = model(preprocessed_image)
    except: 
        predictions = model.predict(preprocessed_image)

    gc.collect()

    return predictions

# Alternative to numpy.argmax 
def argmax(result):
    if len(result) == 1: # When list is nested
        return max(range(len(result[0])), key=result[0].__getitem__)
    else: 
        return max(range(len(result)), key=result.__getitem__)

def process_image(image_content, model, preprocess_input, target_size):
    # Predict on the image, used for the front classification

    result_prediction = str(argmax(predict_on_image(image_content, model, preprocess_input, target_size)))

    gc.collect()
    
    # Return a dictionary or any other data you want
    return {"status": "success", "result": result_prediction}

def img_prediction_model_pnns(image_content, pnns_groups, model, preprocess_input, target_size):
    # Predict pnns group

    if pnns_groups == "pnns_groups_1":
        list_pnns = ['Composite foods', 'Fruits and vegetables', 'Cereals and potatoes', 'Fat and sauces',
                    'Salty snacks', 'Beverages', 'Sugary snacks', 'Fish Meat Eggs', 'Milk and dairy products']
    
    elif pnns_groups == "pnns_groups_2":
        list_pnns = ['Pizza pies and quiches', 'Fruits', 'Bread', 'Dressings and sauces', 'Salty and fatty products',
                     'Sweetened beverages', 'Sweets', 'Biscuits and cakes', 'Pastries', 'Fish and seafood',
                     'One-dish meals', 'Appetizers', 'Cheese', 'Fats', 'Processed meat', 'Sandwiches',
                     'Vegetables', 'Breakfast cereals', 'Chocolate products', 'Unsweetened beverages',
                     'Dried fruits', 'Meat', 'Cereals', 'Eggs', 'Plant-based milk substitutes', 'Legumes',
                     'Teas and herbal teas and coffees', 'Dairy desserts', 'Nuts', 'Fruit juices',
                     'Milk and yogurt', 'Artificially sweetened beverages', 'Potatoes', 'Soups', 'Ice cream',
                     'Offals', 'Waters and flavored waters', 'Fruit nectars']

    result = predict_on_image(image_content, model, preprocess_input, target_size)
    
    image_proba = []
    
    for pnns, proba in zip(list_pnns, result[0]):
        image_proba.append([pnns, proba])
        
    # Using a list of dictionaries
    result = tf.unstack(result)[0].numpy().tolist() if isinstance(result, tf.Tensor) else result.tolist()
    
    #image_proba = list(zip(list_pnns, result[0].tolist()))
    image_proba = list(zip(list_pnns, result))

    image_proba.sort(key=lambda x: x[1], reverse=True)

    # Convert the sorted list of tuples to a list of dictionaries
    image_proba = [{"pnns_groups": pnns, "probabilities": proba} for pnns, proba in image_proba]
    
    del result
    gc.collect()

    return image_proba

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
