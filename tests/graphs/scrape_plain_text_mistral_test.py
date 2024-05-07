"""
Module for the tests
"""
import os
import pytest
from scrapegraphai.graphs import SmartScraperGraph


@pytest.fixture
def sample_text():
    """
    Example of text
    """
    file_name = "inputs/plain_html_example.txt"
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(curr_dir, file_name)

    with open(file_path, 'r', encoding="utf-8") as file:
        text = file.read()

    return text


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
        },
        "embeddings": {
            "model": "ollama/nomic-embed-text",
            "temperature": 0,
            "base_url": "http://localhost:11434",
        }
    }


def test_scraping_pipeline(sample_text: str, graph_config: dict):
    """
    Start of the scraping pipeline
    """
    smart_scraper_graph = SmartScraperGraph(
        prompt="List me all the news with their description.",
        source=sample_text,
        config=graph_config
    )

    result = smart_scraper_graph.run()

    assert result is not None
