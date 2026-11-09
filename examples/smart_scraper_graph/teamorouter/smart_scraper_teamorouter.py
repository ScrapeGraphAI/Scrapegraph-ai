"""
Basic example of scraping pipeline using SmartScraper with TeamoRouter
"""

import json
import os

from dotenv import load_dotenv

from scrapegraphai.graphs import SmartScraperGraph
from scrapegraphai.utils import prettify_exec_info

load_dotenv()

# ************************************************
# Define the configuration for the graph
# ************************************************

graph_config = {
    "llm": {
        "api_key": os.getenv("TEAMOROUTER_API_KEY"),
        # Any chat model id from https://api.teamorouter.com/v1/models,
        # prefixed with "teamorouter/".
        "model": "teamorouter/deepseek-v4-flash",
    },
    "verbose": True,
    "headless": True,
}

# ************************************************
# Create the SmartScraperGraph instance and run it
# ************************************************

smart_scraper_graph = SmartScraperGraph(
    prompt="List the first 5 books with their title and price",
    source="https://books.toscrape.com/",
    config=graph_config,
)

result = smart_scraper_graph.run()
print(json.dumps(result, indent=4))

# ************************************************
# Get graph execution info
# ************************************************

graph_exec_info = smart_scraper_graph.get_execution_info()
print(prettify_exec_info(graph_exec_info))
