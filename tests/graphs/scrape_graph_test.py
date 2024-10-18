"""
Module for testing the scrape graph class
"""

import os
import pytest
import pandas as pd
from dotenv import load_dotenv
from scrapegraphai.graphs import ScrapeGraph
from scrapegraphai.utils import prettify_exec_info

load_dotenv()

@pytest.fixture
def graph_config():
    """Configuration of the graph"""
    openai_key = os.getenv("OPENAI_APIKEY")
    return {
        "llm": {
            "api_key": openai_key,
            "model": "openai/gpt-3.5-turbo",
        },
        "verbose": True,
        "headless": False,
    }

def test_scraping_pipeline(graph_config):
    """Start of the scraping pipeline"""
    scrape_graph = ScrapeGraph(
        source="https://perinim.github.io/projects/",
        config=graph_config,
    )

    result = scrape_graph.run()

    assert result is not None
    assert isinstance(result, list)

def test_get_execution_info(graph_config):
    """Get the execution info"""
    scrape_graph = ScrapeGraph(
        source="https://perinim.github.io/projects/",
        config=graph_config,
    )

    scrape_graph.run()

    graph_exec_info = scrape_graph.get_execution_info()

    assert graph_exec_info is not None
