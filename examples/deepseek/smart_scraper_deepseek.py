""" 
Basic example of scraping pipeline using SmartScraper
"""
import os
from dotenv import load_dotenv
from scrapegraphai.graphs import SmartScraperGraph
from scrapegraphai.utils import prettify_exec_info

load_dotenv()

# ************************************************
# Define the configuration for the graph
# ************************************************

deepseek_key = os.getenv("DEEPSEEK_APIKEY")

graph_config = {
    "llm": {
        "model": "deepseek/deepseek-chat",
        "api_key": deepseek_key,
    },
    "verbose": True,
}

# ************************************************
# Create the SmartScraperGraph instance and run it
# ************************************************

smart_scraper_graph = SmartScraperGraph(
    prompt="List me all the projects with their description.",
    # also accepts a string with the already downloaded HTML code
    source="https://perinim.github.io/projects/",
    config=graph_config
)

result = smart_scraper_graph.run()
print(result)

# ************************************************
# Get graph execution info
# ************************************************

graph_exec_info = smart_scraper_graph.get_execution_info()
print(prettify_exec_info(graph_exec_info))
