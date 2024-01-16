import requests
import concurrent.futures
import logging
import os
import asyncio

# Set up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__) 

def get_image(code, number = 1):
    # Transform the code to produce the Open Food Facts image URL
    # number = the image we choose to retrieve
    if len(code) <= 8:
        url = f'https://images.openfoodfacts.org/images/products/{code}/{number}.jpg'
        return url
    elif len(code) > 8:
        code = "0"*(13 - len(code)) + code
        url = f'https://images.openfoodfacts.org/images/products/{code[:3]}/{code[3:6]}/{code[6:9]}/{code[9:]}/{number}.jpg'
        return url
    else:
        return None

def generate_urls(df):
    """
    Generate urls for the products (image 1 to 4 at 400  pxl)
    Return the modified df
    """

    for i in range(1, 5):
        df[f"image_{i}"] = df.apply(lambda x: get_image(str(x["code"]), number = f"{i}.400"), axis = 1)

    return df


def check_url_image(url):
    """
    Check if the link of the image is correct
    Return none if not
    """
    
    try:
        response = requests.head(url) # We use head instead of get, we only need to check the link
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        return url
    except requests.exceptions.RequestException:
        return None
    
def check_image_urls_parallel(urls, checked_images, failed_img):
    """
    The check_image_urls_parallel function uses concurrent.futures.ThreadPoolExecutor 
    to perform the checks concurrently.
    """
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        #The map function is used to apply the check_url function to each URL in parallel.
        results = executor.map(check_url_image, urls) # return a generator
      
    #The check_url_image function puts the results appropriate queue (checked_queue or failed_queue)
    for result, url in zip(results, urls):
        if result is not None:
            checked_images.add(result)
        else:
            checked_images.add(url)
            failed_img.add(url)

def testing_urls_data(df, checked_images, failed_img):
    total_rows = df.shape[0]

    for image in ["image_1", "image_2", "image_3", "image_4"]:
        print(f"Processing: {total_rows} {image}")
        
        for idx in range(0, total_rows, 100):
            print(f"{idx} urls processed")
            # To show the progression every 1%

            if (idx + 1) % (total_rows // 100) == 0:
                progress_percentage = ((idx + 1) / total_rows) * 100
                print(f"Progression: {progress_percentage:.2f}%")
            try:
                testing_img(df[idx:idx+100][image], checked_images, failed_img)
            except:
                testing_img(df[idx:total_rows][image], checked_images, failed_img)
    return df

def testing_img(urls, checked_images, failed_img):
    to_test = []

    for i, url in enumerate(urls):
        if url not in checked_images:
            to_test.append(url)

    check_image_urls_parallel(to_test, checked_images, failed_img)  