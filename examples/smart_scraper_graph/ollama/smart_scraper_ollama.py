"""
Basic example of scraping pipeline using SmartScraper
"""

from scrapegraphai.graphs import SmartScraperGraph
from scrapegraphai.utils import prettify_exec_info

# ************************************************
# Define the configuration for the graph
# ************************************************

graph_config = {
    "llm": {
        "model": "ollama/llama3.2:3b",
        "temperature": 0,
        # "base_url": "http://localhost:11434", # set ollama URL arbitrarily
        "model_tokens": 4096,
    },
    "verbose": True,
    "headless": False,
}

# ************************************************
# Create the SmartScraperGraph instance and run it
# ************************************************
smart_scraper_graph = SmartScraperGraph(
    prompt="Find some information about what does the company do and the list of founders.",
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
