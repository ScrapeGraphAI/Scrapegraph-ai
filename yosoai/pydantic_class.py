"""
Pydantic module to send
"""
from langchain_core.pydantic_v1 import BaseModel, Field


class _Response(BaseModel):
    title_news: str = Field(description='Give me the name of the news')
