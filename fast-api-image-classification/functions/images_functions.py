from PIL import Image
import tensorflow as tf
import gc
from functions.others_functions import argmax

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