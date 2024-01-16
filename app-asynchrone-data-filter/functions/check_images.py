import requests
import logging
import tqdm
import concurrent.futures
import os

# Set up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)  

# Read environment variable from Heroku config vars
url_api = os.environ.get('URL_API')

if url_api is None:
    raise EnvironmentError("The 'url_api' environment variable is not set.")

# Request retrieving content of url
def retrieve_url_content(url):    
    if not str(url).startswith("http"):
        # No url available
        return None

    try:
        response = requests.get(url)
        return response
    
    except Exception as e:
        logger.error(f"Error retrieving content from URL {url}: {str(e)}")
        return None

# Call the API, sending the image and returning the result (0 or 1)
def model_front_classification(content):
    if content is None or not content:
        # No url 
        return None
    
    # Files will content the information on the image
    files = {"file": ('temp_image.jpg', content, 'image/jpg')}
    
    try:
        # We send images to the API
        response = requests.post(url_api + "/process-image/", files=files)
    except Exception as e:
        logger.info("status: error")
        logger.info(f"message: {str(e)}")
    
    if 'result' in response.json():
        # Return 1 if image is the front and 0 if image is the back
        result = response.json()['result']
        return result

    # It can be an error, so we return nothing and log it
    else:
        return None
    
# Call the API, sending the images in batch and returning a list of 0 and 1
def model_front_classification_batch(contents):
    if contents is None or not contents:
        return None

    # List of files to send to API
    files = [("files", ('temp_image.jpg', content, 'image/jpg')) for content in contents]
    
    try:
        # We send images to the API
        response = requests.post(url_api + "/process-batch-images/", files=files)
    except Exception as e:
        logger.info("status: error")
        logger.info(f"message: {str(e)}")
        response = {"None"}

    # Result are conserved in list
    results = []
    for result in response.json():
        if 'result' in result:
            # Extract results for each image
            results.extend(result['result'])

        else:
            results.append(None)

    return results

def check_type_data_image(df, back_images, type_image):

    if len(back_images) > 0:
        num_concurrent_requests = 20 # Number of concurrent requests   
        num_concurrent_workers = 10 # Number of concurrent workers 
        batch_size = 12 # Number of images sent by batch 
        chunk_size = 50 # Size to send batch   

        initial_df = df[df.index.isin(back_images)]

        # We retrieve the urls 
        urls_image = initial_df[type_image].to_list()

        results_images = []

        # First, we retrieve the contents of the images
        #with concurrent.futures.ThreadPoolExecutor(max_workers=num_concurrent_requests) as executor:
         #   contents = list(tqdm.tqdm(executor.map(retrieve_url, urls_image), total=len(urls_image),
          #                             desc=f"Retrieving contents for {type_image}"))

        # We clean that up
        #if len(contents) > 1:
         #   contents = [content.content if content is not None else "None" for content in contents]

        # Split the contents into batches
        if batch_size < len(urls_image):
            for i in tqdm.tqdm(range(0, len(urls_image), chunk_size), desc=f"Processing {type_image} in chunks"):
                print(i)

                chunk_url_images = urls_image[i:i + chunk_size] if i + chunk_size < len(urls_image) + 1 else urls_image[i:]

                # First, we retrieve the contents of the images
                with concurrent.futures.ThreadPoolExecutor(max_workers=num_concurrent_requests) as executor:
                    contents = list(executor.map(retrieve_url_content, chunk_url_images))
                    # We clean that up
                    if len(contents) > 1:
                        contents = [content.content if content is not None else "None" for content in contents]

                #current_chunk = contents[i:i + chunk_size] if i + chunk_size < len(contents) + 1 else contents[i:]

                content_batches = [contents[idx:idx+batch_size] for idx in range(0, len(contents), batch_size)] if len(contents) > batch_size else [contents]

                #the content_batches to the API, that will return the result into the list
                with concurrent.futures.ProcessPoolExecutor(max_workers=num_concurrent_workers) as executor:
                    results_images.extend(tqdm.tqdm(executor.map(model_front_classification_batch, content_batches), 
                                               total=len(content_batches),
                                               desc=f"Processing contents for {type_image}"))

            # At the end, we flatten the list
            results_images = [num for sublist in results_images for num in sublist]

        else:
            # First, we retrieve the contents of the images
            with concurrent.futures.ThreadPoolExecutor(max_workers=num_concurrent_requests) as executor:
                contents = list(tqdm.tqdm(executor.map(retrieve_url_content, urls_image), total=len(urls_image),
                                            desc=f"Retrieving contents for {type_image}"))
                # We clean that up
                if len(contents) > 1:
                    contents = [content.content if content is not None else "None" for content in contents]

            with concurrent.futures.ProcessPoolExecutor(max_workers=num_concurrent_workers) as executor:
                results_images.extend(tqdm.tqdm(executor.map(model_front_classification, contents),
                                                total=len(contents),
                                                desc=f"Processing single images for {type_image}"))  # image in single
        
        # We retrieve the index of the images that need to be change
        initial_df_index = initial_df.index.to_list()
        index = [i for i, value in enumerate(results_images) if value == "1"]
        front_images = [value for i, value in enumerate(initial_df_index) if i in index]

        logger.info(f"Number of images corresponding to front: '{len(front_images)}'")    

        if type_image != "image_1":
            df.loc[df.index.isin(front_images), ["image_1", type_image]] = df.loc[df.index.isin(front_images), [type_image, "image_1"]].to_numpy()    

        # We retrieve the index of the images that need to be change
        index = [i for i, value in enumerate(results_images) if value != "1"]
        back_images = [value for i, value in enumerate(initial_df_index) if i in index]

        if type_image == "image_4":
            logger.info(f"Number of product(s) with no proper images: '{len(back_images)}'")

            df.loc[df.index.isin(back_images), ["image_1", "image_2", "image_3", "image_4"]] = None

        return df, back_images
    
    else:
        return df, []

# Function checking images_1 in DataFrame of products 
def check_data_image(df):

    logger.info(f"[INFO] A total of {df.shape[0]} images will be processed...")

    logger.info("[INFO] Front/Back classification...")

    image_types = ["image_1", "image_2", "image_3", "image_4"]

    # initialization
    back_images = df.index

    for i, image_type in enumerate(image_types, start=1):
        logger.info(f"[INFO] Processing images {i}...")
        df, back_images = check_type_data_image(df, back_images, image_type)

    logger.info("[INFO] Front/Back classification...Done")
    
    # We return the dataframe
    return df
