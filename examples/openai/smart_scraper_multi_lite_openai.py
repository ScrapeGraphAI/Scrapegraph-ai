""" 
Basic example of scraping pipeline using SmartScraper
"""
import os
import json
from dotenv import load_dotenv
from scrapegraphai.graphs import SmartScraperMultiLiteGraph
from scrapegraphai.utils import prettify_exec_info

load_dotenv()

# ************************************************
# Define the configuration for the graph
# ************************************************


graph_config = {
    "llm": {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "model": "openai/gpt-4o",
    },
    "verbose": True,
    "headless": False,
}

# ************************************************
# Create the SmartScraperGraph instance and run it
# ************************************************

smart_scraper_multi_lite_graph = SmartScraperMultiLiteGraph(
    prompt="Who is Marco Perini?",
    source= [
        "https://perinim.github.io/",
        "https://perinim.github.io/cv/"
    ],
    config=graph_config
)

result = smart_scraper_multi_lite_graph.run()
print(json.dumps(result, indent=4))

# ************************************************
# Get graph execution info
# ************************************************

graph_exec_info = smart_scraper_multi_lite_graph.get_execution_info()
print(prettify_exec_info(graph_exec_info))
