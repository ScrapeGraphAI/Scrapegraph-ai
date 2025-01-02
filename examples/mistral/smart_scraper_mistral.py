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
        "api_key": os.getenv("MISTRAL_API_KEY"),
        "model": "mistralai/open-mistral-nemo",
    },
    "verbose": True,
    "headless": False,
}

# ************************************************
# Create the SmartScraperGraph instance and run it
# ************************************************

smart_scraper_graph = SmartScraperGraph(
    prompt="List me what does the company do, the name and a contact email.",
    source="https://scrapegraphai.com/",
    config=graph_config
)

result = smart_scraper_graph.run()
print(json.dumps(result, indent=4))
