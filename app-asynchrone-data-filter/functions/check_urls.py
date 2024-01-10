import requests
import concurrent.futures
import logging

# Set up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)  

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
        logger.info(f"Processing: {image}")
        
        for idx in range(0, total_rows, 100):
            # To show the progression every 1%
            if (idx + 1) % (total_rows // 100) == 0:
                progress_percentage = ((idx + 1) / total_rows) * 100
                logger.info(f"Progression: {progress_percentage:.2f}%")
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