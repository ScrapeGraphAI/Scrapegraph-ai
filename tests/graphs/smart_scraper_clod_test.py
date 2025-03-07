"""
Module for testing the smart scraper class
"""

import os

import pytest
from dotenv import load_dotenv

from scrapegraphai.graphs import SmartScraperGraph

load_dotenv()


@pytest.fixture
def graph_config():
    """Configuration of the graph"""
    clod_api_key = os.getenv("CLOD_API_KEY")
    return {
        "llm": {
            "api_key": clod_api_key,
            "model": "clod/claude-3-5-sonnet-latest",
        },
        "verbose": True,
        "headless": False,
    }


def test_scraping_pipeline(graph_config):
    """Start of the scraping pipeline"""
    smart_scraper_graph = SmartScraperGraph(
        prompt="List me all the projects with their description.",
        source="https://perinim.github.io/projects/",
        config=graph_config,
    )

    result = smart_scraper_graph.run()

    assert result is not None
    assert isinstance(result, dict)


def test_get_execution_info(graph_config):
    """Get the execution info"""
    smart_scraper_graph = SmartScraperGraph(
        prompt="List me all the projects with their description.",
        source="https://perinim.github.io/projects/",
        config=graph_config,
    )

    smart_scraper_graph.run()

    graph_exec_info = smart_scraper_graph.get_execution_info()

    assert graph_exec_info is not None
