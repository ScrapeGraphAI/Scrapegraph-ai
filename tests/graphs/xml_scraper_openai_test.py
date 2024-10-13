"""
xml_scraper_test
"""
import os
import pytest
from dotenv import load_dotenv
from scrapegraphai.graphs import XMLScraperGraph
from scrapegraphai.utils import convert_to_csv, convert_to_json, prettify_exec_info

load_dotenv()

# ************************************************
# Define the test fixtures and helpers
# ************************************************

@pytest.fixture
def graph_config():
    """
    Configuration for the XMLScraperGraph
    """
    openai_key = os.getenv("OPENAI_APIKEY")
    return {
        "llm": {
            "api_key": openai_key,
            "model": "openai/gpt-4o",
        },
        "verbose": False,
    }

@pytest.fixture
def xml_content():
    """
    Fixture to read the XML file content
    """
    FILE_NAME = "inputs/books.xml"
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(curr_dir, FILE_NAME)

    with open(file_path, 'r', encoding="utf-8") as file:
        return file.read()

# ************************************************
# Define the test cases
# ************************************************

def test_xml_scraper_graph(graph_config: dict, xml_content: str):
    """
    Test the XMLScraperGraph scraping pipeline
    """
    xml_scraper_graph = XMLScraperGraph(
        prompt="List me all the authors, title and genres of the books",
        source=xml_content,  # Pass the XML content
        config=graph_config
    )

    result = xml_scraper_graph.run()

    assert result is not None

def test_xml_scraper_execution_info(graph_config: dict, xml_content: str):
    """
    Test getting the execution info of XMLScraperGraph
    """
    xml_scraper_graph = XMLScraperGraph(
        prompt="List me all the authors, title and genres of the books",
        source=xml_content,  # Pass the XML content
        config=graph_config
    )

    xml_scraper_graph.run()

    graph_exec_info = xml_scraper_graph.get_execution_info()

    assert graph_exec_info is not None
    print(prettify_exec_info(graph_exec_info))

def test_xml_scraper_save_results(graph_config: dict, xml_content: str):
    """
    Test saving the results of XMLScraperGraph to CSV and JSON
    """
    xml_scraper_graph = XMLScraperGraph(
        prompt="List me all the authors, title and genres of the books",
        source=xml_content,  # Pass the XML content
        config=graph_config
    )

    result = xml_scraper_graph.run()

    # Save to csv and json
    convert_to_csv(result, "result")
    convert_to_json(result, "result")

    assert os.path.exists("result.csv")
    assert os.path.exists("result.json")
