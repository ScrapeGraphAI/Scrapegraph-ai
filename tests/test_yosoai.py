import pytest
from yosoai.pydantic_class import _Response
from yosoai.class_creator import create_class
from langchain_openai import ChatOpenAI

@pytest.fixture
def generator():
    values = [
        {"title": "title_website", "type": "str", "description": "Title of the items"},
    ]
    create_class(values)
    return ChatOpenAI(values)

def test_generator_invocation(generator):
    query_info = "Your test query here"
    result = generator.invocation(query_info)
    assert result is not None  
    
def test_response_model():
    # Test the Response Pydantic model
    response_data = {"title_website": "Test Title"}
    response = _Response(**response_data)
    assert response.title_swebsite == "Test Title"