base_script = '''
from langchain_core.pydantic_v1 import BaseModel, Field

class Response(BaseModel):
'''

# This function creates a class at runtime using the values from the list.
def create_class(data_dict: dict):
    for elem in data_dict:
        global base_script
        base_script = base_script + f"    {elem['title']}: {elem['type']} = Field(description='{elem['description']}')\n"

    with open("AmazScraper/pydantic_class.py", "w") as f:
        f.write(base_script)
