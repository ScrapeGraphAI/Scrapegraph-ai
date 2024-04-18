""" 
Module for testing th smart scraper class
"""
import pytest
from scrapegraphai.graphs import SmartScraperGraph


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


def test_scraping_pipeline(graph_config):
    # Crea un'istanza di SmartScraperGraph
    smart_scraper_graph = SmartScraperGraph(
        prompt="List me all the news with their description.",
        source="https://perinim.github.io/projects",
        config=graph_config
    )

    # Esegui il grafico
    result = smart_scraper_graph.run()

    # Verifica che il risultato non sia vuoto
    assert result is not None


def test_get_execution_info(graph_config):
    # Crea un'istanza di SmartScraperGraph
    smart_scraper_graph = SmartScraperGraph(
        prompt="List me all the news with their description.",
        source="https://perinim.github.io/projects",
        config=graph_config
    )

    # Esegui il grafico
    smart_scraper_graph.run()

    # Ottieni le informazioni sull'esecuzione del grafico
    graph_exec_info = smart_scraper_graph.get_execution_info()

    # Verifica che le informazioni sull'esecuzione non siano vuote
    assert graph_exec_info is not None
