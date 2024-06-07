"""
Module for scraping JSON documents
"""
import os
import json
import pytest

from scrapegraphai.graphs import JSONScraperGraph

# Load configuration from a JSON file
CONFIG_FILE = "config.json"
with open(CONFIG_FILE, "r") as f:
    CONFIG = json.load(f)

# Fixture to read the sample JSON file
@pytest.fixture
def sample_json():
    """
    Read the sample JSON file
    """
    file_path = os.path.join(os.path.dirname(__file__), "inputs", "example.json")
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()
    return text

# Parametrized fixture to load graph configurations
@pytest.fixture(params=CONFIG["graph_configs"])
def graph_config(request):
    """
    Load graph configuration
    """
    return request.param

# Test function for the scraping pipeline
def test_scraping_pipeline(sample_json, graph_config):
    """
    Test the scraping pipeline
    """
    expected_titles = ["Title 1", "Title 2", "Title 3"]  # Replace with expected titles

    smart_scraper_graph = JSONScraperGraph(
        prompt="List me all the titles",
        source=sample_json,
        config=graph_config
    )
    result = smart_scraper_graph.run()

    assert result is not None
    assert isinstance(result, list)
    assert sorted(result) == sorted(expected_titles)
