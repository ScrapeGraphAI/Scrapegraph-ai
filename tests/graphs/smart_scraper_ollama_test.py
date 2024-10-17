""" 
Module for testing th smart scraper class
"""
import pytest
from scrapegraphai.graphs import SmartScraperGraph
from transformers import GPT2TokenizerFast


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


def test_gpt2_tokenizer_loading():
    """
    Test loading of GPT2TokenizerFast
    """
    tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
    assert tokenizer is not None
