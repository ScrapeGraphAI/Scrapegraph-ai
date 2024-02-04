from .getter import remover
from .class_creator import create_class
from .class_generator import Generator

def send_request(values: list[dict]) -> dict: 
    """
    Send a request to openai.

    Args:
        values (list[dict]): Settings of the request. 
                        Each element of the list should have the following keys:
                            - "title" (str): The title of the field.
                            - "type" (str): The type of the field.
                            - "description" (str): The description of the field.

    Returns:
        dict: The result of the request to openai.
    """

    res = {} 
    create_class("TOADD")

    return res