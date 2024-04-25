""" 
Module for making the tests for ScriptGeneratorGraph
"""
import pytest
from scrapegraphai.graphs import ScriptCreatorGraph
from scrapegraphai.utils import prettify_exec_info


@pytest.fixture
def graph_config():
    """
    Configuration of the graph
    """
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


def test_script_creator_graph(graph_config: dict):
    """
    Start of the scraping pipeline
    """
    smart_scraper_graph = ScriptCreatorGraph(
        prompt="List me all the news with their description.",
        source="https://perinim.github.io/projects",
        config=graph_config
    )

    result = smart_scraper_graph.run()

    assert result is not None

    graph_exec_info = smart_scraper_graph.get_execution_info()

    assert graph_exec_info is not None

    assert isinstance(graph_exec_info, dict)

    print(prettify_exec_info(graph_exec_info))
