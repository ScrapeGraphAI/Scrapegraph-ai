"""
Module for testing the smart scraper class
"""

import os
import pytest
import pandas as pd
from dotenv import load_dotenv
from scrapegraphai.graphs import SmartScraperGraph
from scrapegraphai.utils import prettify_exec_info

load_dotenv()

@pytest.fixture
def graph_config():
    """Configuration of the graph"""
    openai_key = os.getenv("OPENAI_APIKEY")
    return {
        "llm": {
            "api_key": openai_key,
            "model": "gpt-3.5-turbo",
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
