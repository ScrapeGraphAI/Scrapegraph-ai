"""
search_graph_openai_test.py module
"""
import os
import pytest
from dotenv import load_dotenv
from scrapegraphai.graphs import SearchGraph

load_dotenv()

# ************************************************
# Define the test fixtures and helpers
# ************************************************

@pytest.fixture
def graph_config():
    """
    Configuration for the SearchGraph
    """
    openai_key = os.getenv("OPENAI_APIKEY")
    return {
        "llm": {
            "api_key": openai_key,
            "model": "openai/gpt-4o",
        },
        "max_results": 2,
        "verbose": True,
    }

# ************************************************
# Define the test cases
# ************************************************

def test_search_graph(graph_config: dict):
    """
    Test the SearchGraph functionality
    """
    search_graph = SearchGraph(
        prompt="List me Chioggia's famous dishes",
        config=graph_config
    )

    result = search_graph.run()

    assert result is not None
    assert len(result) > 0


def test_search_graph_execution_info(graph_config: dict):
    """
    Test getting the execution info of SearchGraph
    """
    search_graph = SearchGraph(
        prompt="List me Chioggia's famous dishes",
        config=graph_config
    )

    search_graph.run()

    graph_exec_info = search_graph.get_execution_info()

    assert graph_exec_info is not None
