"""
Basic example of scraping pipeline using SmartScraper with LiteLLM

Install the extra first: pip install scrapegraphai[litellm]
"""

import os

from dotenv import load_dotenv

from scrapegraphai.graphs import SmartScraperGraph
from scrapegraphai.utils import prettify_exec_info

load_dotenv()

# ************************************************
# Define the configuration for the graph
# ************************************************

# "litellm/<provider>/<model>" routes the call through the LiteLLM SDK, so any
# provider LiteLLM supports works here, e.g. "litellm/anthropic/claude-sonnet-4-6",
# "litellm/vertex_ai/gemini-2.5-flash" or "litellm/bedrock/<model id>".
# Credentials are read from the provider's usual environment variables.
graph_config = {
    "llm": {
        "model": os.getenv("LITELLM_MODEL", "litellm/anthropic/claude-sonnet-4-6"),
        "temperature": 0,
    },
    "verbose": True,
    "headless": False,
}

# ************************************************
# Create the SmartScraperGraph instance and run it
# ************************************************

smart_scraper_graph = SmartScraperGraph(
    prompt="Find some information about the founders.",
    source="https://scrapegraphai.com/",
    config=graph_config,
)

result = smart_scraper_graph.run()
print(result)

# ************************************************
# Get graph execution info
# ************************************************

graph_exec_info = smart_scraper_graph.get_execution_info()
print(prettify_exec_info(graph_exec_info))
