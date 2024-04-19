""" 
Module for making the tests for ScriptGeneratorGraph
"""
import pytest
from scrapegraphai.graphs import ScriptCreatorGraph
from scrapegraphai.utils import prettify_exec_info


@pytest.fixture
def graph_config():
    return {
        "llm": {
            "model": "ollama/mistral",
            "temperature": 0,
            "format": "json",
            "base_url": "http://localhost:11434",
            "library": "beautifoulsoup",
        },
        "embeddings": {
            "model": "ollama/nomic-embed-text",
            "temperature": 0,
            "base_url": "http://localhost:11434",
        },
        "library": "beautifoulsoup"
    }


def test_script_creator_graph(graph_config):
    # Create the ScriptCreatorGraph instance
    smart_scraper_graph = ScriptCreatorGraph(
        prompt="List me all the news with their description.",
        source="https://perinim.github.io/projects",
        config=graph_config
    )

    # Run the graph
    result = smart_scraper_graph.run()

    # Check that the result is not empty
    assert result is not None

    # Get graph execution info
    graph_exec_info = smart_scraper_graph.get_execution_info()

    # Check that execution info is not empty
    assert graph_exec_info is not None

    # Check that execution info is a dictionary
    assert isinstance(graph_exec_info, dict)

    # Print execution info
    print(prettify_exec_info(graph_exec_info))
