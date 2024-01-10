
import os
import pickle
import logging

# Set up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)  

# Load a pickle file
def load_pickle_file(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return pickle.load(f)
    else:
        logger.warning(f"No file present at '{path}'")
        return set() 
    
# Create a pickle file
def create_pickle_file(object, path):
    with open(path, 'wb') as file:
        pickle.dump(object, file)

# Function to remove the files downloaded
def remove_local_file(file_path):
    try:
        if os.path.exists(file_path):
            # Remove local object
            os.remove(file_path)
            logger.info(f"Removing file '{file_path}'")
        else: 
            logger.warning(f"No file present at '{file_path}'")
    except Exception as e:
        logger.error(f"Error removing file '{file_path}': {str(e)}")
