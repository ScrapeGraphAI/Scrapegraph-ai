""" 
Basic example of scraping pipeline using SmartScraper
"""
import os
import json
from dotenv import load_dotenv
from scrapegraphai.graphs import SmartScraperMultiConcatGraph

load_dotenv()

# ************************************************
# Define the configuration for the graph
# ************************************************
graph_config = {
    "llm": {
        "api_key": os.getenv("MISTRAL_API_KEY"),
        "model": "mistralai/open-mistral-nemo",
    },
    "verbose": True,
    "headless": False,
}

# *******************************************************
# Create the SmartScraperMultiGraph instance and run it
# *******************************************************

multiple_search_graph = SmartScraperMultiConcatGraph(
    prompt="Who is Marco Perini?",
    source= [
        "https://perinim.github.io/",
        "https://perinim.github.io/cv/"
        ],
    schema=None,
    config=graph_config
)

result = multiple_search_graph.run()
print(json.dumps(result, indent=4))
