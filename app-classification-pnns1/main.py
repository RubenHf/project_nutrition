from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from io import BytesIO
import base64
import tensorflow as tf
from functions.loading_models import load_API_models

app = FastAPI()

# We load the models and the preprocess
loaded_model_pnns1, loaded_model_pnns2, loaded_preprocess_input = load_API_models()

def preprocess_image(image, preprocess_input):
    # Apply the same preprocessing as during training
    # You can use the preprocess_input function from your original project
    # If preprocess_input is not available, you can apply any necessary preprocessing
    return preprocess_input(image)

def load_and_preprocess_image(image_path, preprocess_input):
    # Load and preprocess a single image
    img = tf.keras.preprocessing.image.load_img(image_path, target_size=(299, 299))
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0)  # Create batch dimension
    return preprocess_image(img_array, preprocess_input)

def predict_on_image(model, image_path, preprocess_input):
    preprocessed_image = load_and_preprocess_image(image_path, preprocess_input)
    predictions = model.predict(preprocessed_image)
    return predictions

def img_prediction_model_pnns(model_pnns, pnns_groups, image, preprocess_input):
    
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

    result = predict_on_image(model_pnns, image, preprocess_input)
    
    image_proba = []
    
    for pnns, proba in zip(list_pnns, result[0]):
        image_proba.append([pnns, proba])

    # Using a list of dictionaries
    image_proba = list(zip(list_pnns, result[0].tolist()))
    image_proba.sort(key=lambda x: x[1], reverse=True)

    # Convert the sorted list of tuples to a list of dictionaries
    image_proba = [{"pnns_groups": pnns, "probabilities": proba} for pnns, proba in image_proba]
    
    return image_proba

# Alternative to numpy.argmax 
def argmax(result):
    return max(range(len(result)), key=result.__getitem__)

def process_image(file_contents: bytes, file_extension: str):

    result = predict_on_image(loaded_model, BytesIO(file_contents), loaded_preprocess_input)

    #result = np.argmax(result)
    result = argmax(result)
    
    # Return a dictionary or any other data you want
    return {"status": "success", "result": str(result)}

@app.post("/process-image/")
async def process_image_endpoint(
    file: UploadFile = File(None), 
    base64_image: str = Form(None), 
    pnns_groups: str = Form(None)):

    try:
        if file:
        # If file image is provided, decode it

            # Uploaded file as to be one of those extension
            if file.content_type not in ["image/png", "image/jpeg", "image/jpg"]:
                raise ValueError("Only PNG, JPEG or JPG images are allowed.")

            # Read the file content
            file_contents = await file.read()


        elif base64_image:
        # If base64 image is provided, we decode it

            data_split = base64_image.split('base64,')
            
            encoded_data = data_split[1]
            
            file_contents = base64.b64decode(encoded_data)

        # We do the prediction
        if pnns_groups == "pnns_groups_1":
            result = img_prediction_model_pnns(loaded_model_pnns1, pnns_groups, BytesIO(file_contents), loaded_preprocess_input)
        elif pnns_groups == "pnns_groups_2":
            result = img_prediction_model_pnns(loaded_model_pnns2, pnns_groups, BytesIO(file_contents), loaded_preprocess_input)
        
        #df_result = df_result.to_dict(orient='records')
        return JSONResponse(content=result)

    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)})
