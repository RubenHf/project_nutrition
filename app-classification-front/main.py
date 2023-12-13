from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from PIL import Image
from io import BytesIO
import tensorflow as tf
import pickle

import numpy as np


app = FastAPI()

## I load a model developped to determine if the image is appropriate (Front or back)

def load_model(model_save_path):
    model = tf.keras.models.load_model(model_save_path)
    with open("preprocess_input.pkl", "rb") as f:
        preprocess_input = pickle.load(f)
    return model, preprocess_input

loaded_model, loaded_preprocess_input = load_model("model/model_best_weights.h5")

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



def process_image(file_contents: bytes, file_extension: str):
    # Process the image here
    # For demonstration purposes, just convert it to grayscale
    image = Image.open(BytesIO(file_contents))

    result = predict_on_image(loaded_model, BytesIO(file_contents), loaded_preprocess_input)
    
    result = np.argmax(result)
    
    # Return a dictionary or any other data you want
    return {"status": "success", "result": str(result)}


@app.post("/process-image/")
async def process_image_endpoint(file: UploadFile = File(...)):
    try:
        # Uploaded file as to be one of those extension
        if file.content_type not in ["image/png", "image/jpeg", "image/jpg"]:
            raise ValueError("Only PNG, JPEG or JPG images are allowed.")

        # Read the file content
        file_contents = await file.read()

        # Get the file extension (png or jpeg)
        file_extension = file.content_type.split("/")[-1]

        # Process the image
        result = process_image(file_contents, file_extension)

        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)})
