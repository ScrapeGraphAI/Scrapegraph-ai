""" 
Basic example of scraping pipeline using SmartScraper
"""

import os, json
from scrapegraphai.graphs import SmartScraperGraph
from scrapegraphai.utils import prettify_exec_info


# ************************************************
# Define the configuration for the graph
# ************************************************


graph_config = {
    "llm": {
        "api_key": "s",
        "model": "gpt-3.5-turbo",
    },
    "verbose": True,
    "headless": False,
}

# ************************************************
# Create the SmartScraperGraph instance and run it
# ************************************************

smart_scraper_graph = SmartScraperGraph(
    prompt="Extract me the python code inside the page",
    source="https://www.exploit-db.com/exploits/51447",
    config=graph_config
)

result = smart_scraper_graph.run()
print(json.dumps(result, indent=4))

# ************************************************
# Get graph execution info
# ************************************************

graph_exec_info = smart_scraper_graph.get_execution_info()
print(prettify_exec_info(graph_exec_info))
