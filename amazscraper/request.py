from amazscraper.getter import remover
from .class_creator import create_class
from amazscraper.class_generator import Generator


def send_request(values:list[dict]) ->dict: 
    """
    Param:
        values (list[dict]): settings of the request. 
        Format: 
        [
          dict {
                "title": str
                "type": str,
                "description": str
            }
        ]
      
    Return:
        dict: the result of the request to openai
    """
    res =  {} 
    create_class("TOADD")

    return res