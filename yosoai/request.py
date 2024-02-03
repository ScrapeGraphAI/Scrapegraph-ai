from .getter import remover
from .class_creator import create_class
from .class_generator import Generator

def send_request(values: list[dict]) -> dict: 
    """
    Send a request to openai.

    Args:
        values (list[dict]): Settings of the request. 
            Format: 
            [
                {
                    "title": str,
                    "type": str,
                    "description": str
                }
            ]

    Returns:
        dict: The result of the request to openai.
    """

    res = {} 
    create_class("TOADD")

    return res