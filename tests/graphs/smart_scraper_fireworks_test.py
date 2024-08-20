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
    fireworks_api_key = os.getenv("FIREWORKS_APIKEY")  
    return {
        "llm": {
            "api_key": fireworks_api_key,
            "model": "fireworks/accounts/fireworks/models/mixtral-8x7b-instruct"
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
