import time

def create_class(data_dict: dict):
    """
    This function creates a class at runtime using the values from the list.

    Args:
        data_dict (dict): A dictionary containing the description of the prompt.
            It should have the following keys:
                - "title" (str): The title of the field.
                - "type" (str): The type of the field.
                - "description" (str): The description of the field.

    Returns:
        None
    """

    base_script = """
from langchain_core.pydantic_v1 import BaseModel, Field

class _Response(BaseModel):
    """
    
    for elem in data_dict:
        base_script = base_script + f"    {elem['title']}: {elem['type']} = Field(description='{elem['description']}')\n"

    with open("./pydantic_class.py", "w") as f:
        f.write(base_script)