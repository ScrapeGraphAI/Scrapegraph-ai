"""
Module for the tests
"""
import os
import pytest
from scrapegraphai.graphs import SmartScraperGraph


@pytest.fixture
def sample_text():
    # Read the sample text file
    file_name = "inputs/plain_html_example.txt"
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(curr_dir, file_name)

    with open(file_path, 'r', encoding="utf-8") as file:
        text = file.read()

    return text


@pytest.fixture
def graph_config():
    return {
        "llm": {
            "model": "ollama/mistral",
            "temperature": 0,
            "format": "json",
            "base_url": "http://localhost:11434",
        },
        "embeddings": {
            "model": "ollama/nomic-embed-text",
            "temperature": 0,
            "base_url": "http://localhost:11434",
        }
    }


def test_scraping_pipeline(sample_text, graph_config):
    # Create the SmartScraperGraph instance
    smart_scraper_graph = SmartScraperGraph(
        prompt="List me all the news with their description.",
        source=sample_text,
        config=graph_config
    )

    # Run the graph
    result = smart_scraper_graph.run()

    # Check that the result is not empty
    assert result is not None
