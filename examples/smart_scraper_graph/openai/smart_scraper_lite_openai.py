"""
Basic example of scraping pipeline using SmartScraper
"""

import json
import os

from dotenv import load_dotenv

from scrapegraphai.graphs import SmartScraperLiteGraph
from scrapegraphai.utils import prettify_exec_info

load_dotenv()

graph_config = {
    "llm": {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "model": "openai/gpt-4o",
    },
    "verbose": True,
    "headless": False,
}

smart_scraper_lite_graph = SmartScraperLiteGraph(
    prompt="Who is ?",
    source="https://perinim.github.io/",
    config=graph_config,
)

result = smart_scraper_lite_graph.run()
print(json.dumps(result, indent=4))

graph_exec_info = smart_scraper_lite_graph.get_execution_info()
print(prettify_exec_info(graph_exec_info))
