""" 
Module for testing th smart scraper class
"""
import pytest
from scrapegraphai.graphs import SmartScraperGraph


@pytest.fixture
def graph_config():
    """
    Configuration of the graph
    """
    return {
        "llm": {
            "model": "ernie-bot-turbo",
            "ernie_client_id": "<ernie_client_id>",
            "ernie_client_secret": "<ernie_client_secret>",
            "temperature": 0.1
        }
    }


def test_scraping_pipeline(graph_config: dict):
    """
    Start of the scraping pipeline
    """
    smart_scraper_graph = SmartScraperGraph(
        prompt="List me all the news with their description.",
        source="https://perinim.github.io/projects",
        config=graph_config
    )

    result = smart_scraper_graph.run()

    assert result is not None


def test_get_execution_info(graph_config: dict):
    """
    Get the execution info
    """
    smart_scraper_graph = SmartScraperGraph(
        prompt="List me all the news with their description.",
        source="https://perinim.github.io/projects",
        config=graph_config
    )

    smart_scraper_graph.run()

    graph_exec_info = smart_scraper_graph.get_execution_info()

    assert graph_exec_info is not None
