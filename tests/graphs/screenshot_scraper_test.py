import os
import pytest
import json
from scrapegraphai.graphs import ScreenshotScraperGraph
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Define a fixture for the graph configuration
@pytest.fixture
def graph_config():
    """
    Creation of the graph
    """
    return {
        "llm": {
            "api_key": os.getenv("OPENAI_API_KEY"),
            "model": "gpt-4o",
        },
        "verbose": True,
        "headless": False,
    }

def test_screenshot_scraper_graph(graph_config):
    """
    test
    """
    smart_scraper_graph = ScreenshotScraperGraph(
        prompt="List me all the projects",
        source="https://perinim.github.io/projects/",
        config=graph_config
    )

    result = smart_scraper_graph.run()

    assert result is not None, "The result should not be None"

    print(json.dumps(result, indent=4))
