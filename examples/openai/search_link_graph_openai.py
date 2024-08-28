""" 
Basic example of scraping pipeline using SmartScraper
"""

import os
from dotenv import load_dotenv
from scrapegraphai.graphs import SearchLinkGraph
from scrapegraphai.utils import prettify_exec_info

load_dotenv()
# ************************************************
# Define the configuration for the graph
# ************************************************

openai_key = os.getenv("OPENAI_APIKEY")

graph_config = {
    "llm": {
        "api_key": openai_key,
        "model": "openai/gpt-4o",
    },
    "verbose": True,
    "headless": False,
}

# ************************************************
# Create the SearchLinkGraph instance and run it
# ************************************************

smart_scraper_graph = SearchLinkGraph(
    source="https://sport.sky.it/nba?gr=www",
    config=graph_config
)

result = smart_scraper_graph.run()
print(result)

# ************************************************
# Get graph execution info
# ************************************************

graph_exec_info = smart_scraper_graph.get_execution_info()
print(prettify_exec_info(graph_exec_info))
