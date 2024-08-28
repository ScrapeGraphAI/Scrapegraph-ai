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

mistral_key = os.getenv("MISTRAL_API_KEY")

graph_config = {
    "llm": {
        "api_key": mistral_key,
        "model": "mistralai/open-mistral-nemo",
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
