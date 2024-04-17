""" 
Module for scraping XML documents
"""
import os
import pytest
from scrapegraphai.graphs import SmartScraperGraph


@pytest.fixture
def sample_xml():
    # Leggi il file XML di esempio
    file_name = "inputs/books.xml"
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


def test_scraping_pipeline(sample_xml, graph_config):
    # Crea un'istanza di SmartScraperGraph
    smart_scraper_graph = SmartScraperGraph(
        prompt="List me all the authors, title and genres of the books",
        source=sample_xml,
        config=graph_config
    )

    # Esegui il grafico
    result = smart_scraper_graph.run()

    # Verifica che il risultato non sia vuoto
    assert result is not None
