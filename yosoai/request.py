import time
from tqdm import tqdm 
from typing import List
from multiprocessing import Pool
from tqdm import tqdm  # Import tqdm for progress bar
from .getter import remover
from .class_generator import Generator
from .class_creator import create_class
from .token_calculator import truncate_text_tokens

EMBEDDING_ENCODING = 'cl100k_base'

LAST_REQUEST_TIME = 0
REQUEST_INTERVAL = 20  # Adjust as needed, represents the interval in seconds between requests

def send_request(key: str, text:str, values:list[dict], model:str, temperature:float = 0.0, encoding_name: str = EMBEDDING_ENCODING) -> List[dict]:
    """
    Send a request to openai.
    Args:
        key (str): The API key for accessing the language model.
        text (str): The input text to be processed.
        values (list[dict]): Settings of the request. 
                        Each element of the list should have the following keys:
                            - "title" (str): The title of the field.
                            - "type" (str): The type of the field.
                            - "description" (str): The description of the field.
        model (str): The name of the language model to be used.
        temperature (float): A parameter controlling the randomness of the language model's output (default: 0).
        encoding_name (str): The name of the encoding to be used (default: EMBEDDING_ENCODING).
    Returns:
        List[dict]: The result of the request to openai.
    """

    global LAST_REQUEST_TIME

    res = []
    create_class(values)
    time.sleep(2)  # TODO: implement asynchronous waiting

    messages = truncate_text_tokens(text.replace("\\n", ""), model, encoding_name)
    
    processed_messages = 0

    with tqdm(total=len(messages)) as pbar:
        for message in messages:
            current_time = time.time()
            time_since_last_request = current_time - LAST_REQUEST_TIME
            if time_since_last_request < REQUEST_INTERVAL:
                time.sleep(REQUEST_INTERVAL - time_since_last_request)
            
            generator_instance = Generator(key, temperature, model)

            res.append(generator_instance.invocation(message))
            processed_messages += 1
            pbar.update(1) 

            LAST_REQUEST_TIME = time.time()  

    return res
