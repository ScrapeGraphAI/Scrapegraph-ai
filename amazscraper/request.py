import time
from typing import List
from amazscraper.getter import remover
from amazscraper.class_generator import Generator
from amazscraper.class_creator import create_class
from amazscraper.token_calculator import truncate_text_tokens

EMBEDDING_ENCODING = 'cl100k_base'

def send_request(key: str, text:str, values:list[dict], model:str, temperature:float = 0, encoding_name: str = EMBEDDING_ENCODING) -> List[dict]: 
    """
    Param:
        key (str): openaikey
        text (str): text to scrape 
        values (list[dict]): settings of the request. 
        Format: 
        [
          dict {
                "title": str
                "type": str,
                "description": str
            }
        ]
        encoding_name (str): encoding type
      
    Return:
        List[dict]: the result of the request to openai
    """
    res =  [] 
    create_class(values)
    #We should implement an asynchrous wait instead for the writing part
    time.sleep(2)

    messages = truncate_text_tokens(text, model, encoding_name)
    
    count = 0

    for message in messages:
        generator_instance = Generator(key, temperature, model)

        res.append(generator_instance.invocation(message))

        print(res)
        print(f"Percentage: {round(count/len(messages),2)*100}%")
        count +=1

    return res