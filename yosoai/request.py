import time
from typing import List
from .getter import remover
from .class_creator import create_class
from .class_generator import Generator
from .token_calculator import truncate_text_tokens

EMBEDDING_ENCODING = 'cl100k_base'

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

    res = []
    create_class(values)
    time.sleep(2) # TODO: implement an asynchrous waiting

    text = remover(text)

    messages = truncate_text_tokens(text, model, encoding_name)
    
    count = 0

    for message in messages:
        generator_instance = Generator(key, temperature, model)

        res.append(generator_instance.invocation(message))

        print(res)
        print(f"Percentage: {round(count/len(messages),2)*100}%")
        count +=1

    return res