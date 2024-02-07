import time
from typing import List
from multiprocessing import Pool
from tqdm import tqdm  # Import tqdm for progress bar
from .getter import remover
from .class_generator import Generator
from .class_creator import create_class
from .token_calculator import truncate_text_tokens

EMBEDDING_ENCODING = 'cl100k_base'

def process_message(args):
    key, temperature, model, encoding_name, message = args
    generator_instance = Generator(key, temperature, model)
    result = generator_instance.invocation(message)
    return result

def send_request(key: str, text: str, values: list[dict], model: str, temperature: float = 0.0, encoding_name: str = EMBEDDING_ENCODING) -> List[dict]:
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
    res = []
    create_class(values)
    time.sleep(2) # TODO: implement asynchronous waiting

    # text = remover(text)

    messages = truncate_text_tokens(text, model, encoding_name)
    total_messages = len(messages)
    processed_messages = 0

    pool = Pool(processes=2) # Limit the number of processes to 3

    with tqdm(total=total_messages) as pbar:
        for result in pool.imap_unordered(process_message, [(key, temperature, model, encoding_name, message) for message in messages]):
            res.append(result)
            processed_messages += 1
            pbar.update(1)  # Update the progress bar
            progress = processed_messages / total_messages * 100

            # Wait for 20 seconds between requests to respect the limit
            if processed_messages % 2 == 0:
                time.sleep(20)

    pool.close()
    pool.join()

    return res
