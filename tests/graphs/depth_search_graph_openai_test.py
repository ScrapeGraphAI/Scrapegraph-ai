"""
depth_search_graph test
"""
import os
import pytest
from dotenv import load_dotenv
from scrapegraphai.graphs import DepthSearchGraph

load_dotenv()

@pytest.fixture
def graph_config():
    """
    Configuration for the DepthSearchGraph
    """
    openai_key = os.getenv("OPENAI_APIKEY")
    return {
        "llm": {
            "api_key": openai_key,
            "model": "openai/gpt-4o-mini",
        },
        "verbose": True,
        "headless": False,
        "depth": 2,
        "only_inside_links": False,
    }

def test_depth_search_graph(graph_config: dict):
    """
    Test the DepthSearchGraph scraping pipeline
    """
    search_graph = DepthSearchGraph(
        prompt="List me all the projects with their description",
        source="https://perinim.github.io",
        config=graph_config
    )

    result = search_graph.run()

    assert result is not None


def test_depth_search_execution_info(graph_config: dict):
    """
    Test getting the execution info of DepthSearchGraph
    """
    search_graph = DepthSearchGraph(
        prompt="List me all the projects with their description",
        source="https://perinim.github.io",
        config=graph_config
    )

    search_graph.run()

    graph_exec_info = search_graph.get_execution_info()

    assert graph_exec_info is not None
