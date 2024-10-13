"""
code_generator_graph_openai_test module
"""
import os
from typing import List
import pytest
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from scrapegraphai.graphs import CodeGeneratorGraph

load_dotenv()

# ************************************************
# Define the output schema for the graph
# ************************************************

class Project(BaseModel):
    title: str = Field(description="The title of the project")
    description: str = Field(description="The description of the project")

class Projects(BaseModel):
    projects: List[Project]

@pytest.fixture
def graph_config():
    """
    Configuration for the CodeGeneratorGraph
    """
    openai_key = os.getenv("OPENAI_APIKEY")
    return {
        "llm": {
            "api_key": openai_key,
            "model": "openai/gpt-4o-mini",
        },
        "verbose": True,
        "headless": False,
        "reduction": 2,
        "max_iterations": {
            "overall": 10,
            "syntax": 3,
            "execution": 3,
            "validation": 3,
            "semantic": 3
        },
        "output_file_name": "extracted_data.py"
    }

def test_code_generator_graph(graph_config: dict):
    """
    Test the CodeGeneratorGraph scraping pipeline
    """
    code_generator_graph = CodeGeneratorGraph(
        prompt="List me all the projects with their description",
        source="https://perinim.github.io/projects/",
        schema=Projects,
        config=graph_config
    )

    result = code_generator_graph.run()

    assert result is not None


def test_code_generator_execution_info(graph_config: dict):
    """
    Test getting the execution info of CodeGeneratorGraph
    """
    code_generator_graph = CodeGeneratorGraph(
        prompt="List me all the projects with their description",
        source="https://perinim.github.io/projects/",
        schema=Projects,
        config=graph_config
    )

    code_generator_graph.run()

    graph_exec_info = code_generator_graph.get_execution_info()

    assert graph_exec_info is not None
