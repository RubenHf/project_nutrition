from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from io import BytesIO
import base64
import tensorflow as tf
import pickle
import pandas as pd

import numpy as np

app = FastAPI()


## I load a model developped to determine if the image is appropriate (Front or back)

def load_model(model_save_path):
    model = tf.keras.models.load_model(model_save_path)
    with open("model/preprocess_input.pkl", "rb") as f:
        preprocess_input = pickle.load(f)
    return model, preprocess_input

loaded_model, loaded_preprocess_input = load_model("model/model_classification_best_weights.h5")

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

def img_prediction_model_pnns(model_pnns, image, preprocess_input):
    
    list_pnns = ['Composite foods', 'Fruits and vegetables', 'Cereals and potatoes', 'Fat and sauces',
                    'Salty snacks', 'Beverages', 'Sugary snacks', 'Fish Meat Eggs', 'Milk and dairy products']
        
    result = predict_on_image(model_pnns, image, preprocess_input)
    
    image_proba = []
    
    for pnns, proba in zip(list_pnns, result[0]):
        image_proba.append([pnns, proba])

    image_proba = pd.DataFrame(image_proba, columns=["pnns_groups_2", "probabilities"])
    
    image_proba.sort_values("probabilities", ascending = False, inplace = True)
    
    return image_proba

def process_image(file_contents: bytes, file_extension: str):

    result = predict_on_image(loaded_model, BytesIO(file_contents), loaded_preprocess_input)

    result = np.argmax(result)

    # Return a dictionary or any other data you want
    return {"status": "success", "result": str(result)}

def best_predictions(model_pnns, file_contents: bytes, preprocess_input, threshold = 1):
    image_proba_df = img_prediction_model_pnns(model_pnns, BytesIO(file_contents), preprocess_input)
    
    # We filter on the threshold (we want the pnns with a cummulated proba of "threshold")
    index = image_proba_df[image_proba_df["probabilities"].cumsum() <= threshold].index
    
    image_proba_df = image_proba_df[image_proba_df.index.isin(index)]
    
    return image_proba_df

@app.post("/process-image/")
async def process_image_endpoint(file: UploadFile = File(None), 
    base64_image: str = Form(None)):

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
        df_result = best_predictions(loaded_model, file_contents, loaded_preprocess_input)

        df_result = df_result.to_dict(orient='records')

        return JSONResponse(content=df_result)

    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)})
