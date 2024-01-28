import logging

# Set up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the input shape of the model

def get_model_input_size(model):
    input_shape = model.layers[0].input_shape[0][1:3]

    logger.info(f"Input shape of model: {input_shape}")
    
    return input_shape

# Alternative to numpy.argmax 
def argmax(result):
    if len(result) == 1: # When list is nested
        return max(range(len(result[0])), key=result[0].__getitem__)
    else: 
        return max(range(len(result)), key=result.__getitem__)