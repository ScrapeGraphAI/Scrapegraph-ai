from langchain_core.pydantic_v1 import BaseModel, Field

class _Response(BaseModel):
    title: str = Field(description='Title of the news')
