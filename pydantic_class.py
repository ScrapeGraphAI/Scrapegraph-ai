
from langchain_core.pydantic_v1 import BaseModel, Field

class Response(BaseModel):
    title_swebsite: str = Field(description='Title of the items')
