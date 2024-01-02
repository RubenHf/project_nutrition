from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from PIL import Image
from io import BytesIO
import tensorflow as tf
from functions.loading_models import load_API_models

app = FastAPI()

# We load the model and the preprocess
loaded_model, loaded_preprocess_input = load_API_models()

def load_and_preprocess_image(image_path, preprocess_input):
    # Load and preprocess a single image
    with tf.keras.preprocessing.image.load_img(image_path, target_size=(299, 299)) as img:
        #img = tf.keras.preprocessing.image.load_img(image_path, target_size=(299, 299))
        img_array = tf.keras.preprocessing.image.img_to_array(img)
        img_array = tf.expand_dims(img_array, 0)  # Create batch dimension
        return preprocess_input(img_array)

def predict_on_image(model, image_path, preprocess_input):
    preprocessed_image = load_and_preprocess_image(image_path, preprocess_input)
    predictions = model.predict(preprocessed_image)
    return predictions

# Alternative to numpy.argmax 
def argmax(result):
    if len(result) == 1: # When list is nested
        return max(range(len(result[0])), key=result[0].__getitem__)
    else: 
        return max(range(len(result)), key=result.__getitem__)

def process_image(file_contents: bytes, file_extension: str):
    # Predict on the image

    result = predict_on_image(loaded_model, BytesIO(file_contents), loaded_preprocess_input)

    result_prediction = argmax(result)
    
    # Return a dictionary or any other data you want
    return {"status": "success", "result": str(result_prediction)}


@app.get("/")
def home():
    return {"health_check": "OK"}


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
