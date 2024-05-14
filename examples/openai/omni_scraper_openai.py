""" 
Basic example of scraping pipeline using OmniScraper
"""

import os, json
from dotenv import load_dotenv
from scrapegraphai.graphs import OmniScraperGraph
from scrapegraphai.utils import prettify_exec_info, convert_to_csv

load_dotenv()


# ************************************************
# Define the configuration for the graph
# ************************************************

openai_key = os.getenv("OPENAI_APIKEY")

graph_config = {
    "llm": {
        "api_key": openai_key,
        "model": "gpt-4o",
    },
    "verbose": True,
    "headless": False,
}

# ************************************************
# Create the OmniScraperGraph instance and run it
# ************************************************

omni_scraper_graph = OmniScraperGraph(
    prompt="List me all the projects with their titles and image links and descriptions.",
    # also accepts a string with the already downloaded HTML code
    source="https://perinim.github.io/projects/",
    config=graph_config
)

result = omni_scraper_graph.run()
print(json.dumps(result, indent=2))

# ************************************************
# Get graph execution info
# ************************************************

graph_exec_info = omni_scraper_graph.get_execution_info()
print(prettify_exec_info(graph_exec_info))
