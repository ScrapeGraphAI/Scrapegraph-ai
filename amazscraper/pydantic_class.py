
from langchain_core.pydantic_v1 import BaseModel, Field

class _Response(BaseModel):
    title_website: str = Field(description='Give me the website name')
