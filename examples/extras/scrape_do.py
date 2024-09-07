""" 
Basic example of scraping pipeline using SmartScraper
"""

import os
import json
from dotenv import load_dotenv
from scrapegraphai.graphs import SmartScraperGraph

load_dotenv()

# ************************************************
# Define the configuration for the graph
# ************************************************


graph_config = {
    "llm": {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "model": "openai/gpt-4o",
    },
    "scrape_do": {
        "api_key": os.getenv("SCRAPE_DO_API_KEY"),
    },
    "verbose": True,
    "headless": False,
}

# ************************************************
# Create the SmartScraperGraph instance and run it
# ************************************************

smart_scraper_graph = SmartScraperGraph(
    prompt="List me all the projects",
    source="https://perinim.github.io/projects/",
    config=graph_config
)

result = smart_scraper_graph.run()
print(json.dumps(result, indent=4))
