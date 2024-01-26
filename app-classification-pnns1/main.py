from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from io import BytesIO
import base64
import tensorflow as tf
from functions.loading_models import load_API_models
import gc
import logging

app = FastAPI()

# Set up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)  

# We load the models and the preprocess
loaded_model_pnns1, loaded_model_pnns2, loaded_preprocess_input = load_API_models()

def load_and_preprocess_image(image_path):
    # Load and preprocess a single image
    with tf.keras.preprocessing.image.load_img(image_path, target_size=(299, 299)) as img:
        img_array = tf.keras.preprocessing.image.img_to_array(img)
        img_array = tf.expand_dims(img_array, 0)  # Create batch dimension

        gc.collect()
        # We use the loaded preprocess
        return loaded_preprocess_input(img_array)

def predict_on_image(model, image_path):
    preprocessed_image = load_and_preprocess_image(image_path)
    predictions = model.predict(preprocessed_image)
    gc.collect()
    
    return predictions

def img_prediction_model_pnns(model_pnns, pnns_groups, image):
    
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

    result = predict_on_image(model_pnns, image)
    
    image_proba = []
    
    for pnns, proba in zip(list_pnns, result[0]):
        image_proba.append([pnns, proba])

    # Using a list of dictionaries
    image_proba = list(zip(list_pnns, result[0].tolist()))
    image_proba.sort(key=lambda x: x[1], reverse=True)

    # Convert the sorted list of tuples to a list of dictionaries
    image_proba = [{"pnns_groups": pnns, "probabilities": proba} for pnns, proba in image_proba]
    
    del result
    gc.collect()

    return image_proba

# Alternative to numpy.argmax 
def argmax(result):
    if len(result) == 1: # When list is nested
        return max(range(len(result[0])), key=result[0].__getitem__)
    else: 
        return max(range(len(result)), key=result.__getitem__)

@app.get("/")
def home():
    return {"health_check": "OK"}

@app.post("/process-image/")
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

            data_split = base64_image.split('base64,')
            
            encoded_data = data_split[1]
            
            file_contents = base64.b64decode(encoded_data)

        # We do the prediction on 
            
        logger.info(f"The prediction is done on {pnns_groups}")
        
        if pnns_groups == "pnns_groups_1":
            result = img_prediction_model_pnns(loaded_model_pnns1, pnns_groups, BytesIO(file_contents), loaded_preprocess_input)
        elif pnns_groups == "pnns_groups_2":
            result = img_prediction_model_pnns(loaded_model_pnns2, pnns_groups, BytesIO(file_contents), loaded_preprocess_input)
        
        gc.collect()
        
        logger.info("...successful prediction")

        #df_result = df_result.to_dict(orient='records')
        return JSONResponse(content=result)

    except Exception as e:
        
        logger.info("status: error")
        logger.info(f"message: {str(e)}")

        return JSONResponse(content={"status": "error", "message": str(e)})
