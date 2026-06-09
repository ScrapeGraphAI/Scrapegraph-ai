"""
Basic example of scraping pipeline using SmartScraper with Atlas Cloud.
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
        "api_key": os.getenv("ATLASCLOUD_API_KEY"),
        "model": f'atlascloud/{os.getenv("ATLASCLOUD_MODEL", "deepseek-ai/deepseek-v4-pro")}',
        "model_tokens": int(os.getenv("ATLASCLOUD_MODEL_TOKENS", "131072")),
    },
    "verbose": True,
    "headless": False,
}

# ************************************************
# Create the SmartScraperGraph instance and run it
# ************************************************

smart_scraper_graph = SmartScraperGraph(
    prompt="Extract the product description and primary integrations",
    source="https://scrapegraphai.com/",
    config=graph_config,
)

result = smart_scraper_graph.run()
print(json.dumps(result, indent=4))

# ************************************************
# Get graph execution info
# ************************************************

graph_exec_info = smart_scraper_graph.get_execution_info()
print(prettify_exec_info(graph_exec_info))
