"""
Example of a SmartScraper pipeline running behind a residential proxy.

Any proxy that speaks the standard {server, username, password} format can be
passed through `loader_kwargs.proxy`. This example uses ProxyHat residential
proxies; swap in your own provider's credentials as needed.
"""

import json
import os

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
    "loader_kwargs": {
        "proxy": {
            "server": os.getenv("PROXYHAT_PROXY_SERVER"),
            "username": os.getenv("PROXYHAT_USERNAME"),
            "password": os.getenv("PROXYHAT_PASSWORD"),
        },
    },
    "verbose": True,
    "headless": True,
}

# ************************************************
# Create the SmartScraperGraph instance and run it
# ************************************************

smart_scraper_graph = SmartScraperGraph(
    prompt="List me all the projects with their description",
    source="https://perinim.github.io/projects/",
    config=graph_config,
)

result = smart_scraper_graph.run()
print(json.dumps(result, indent=4))
