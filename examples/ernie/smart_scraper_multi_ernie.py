""" 
Basic example of scraping pipeline using SmartScraper
"""

import os, json
from dotenv import load_dotenv
from scrapegraphai.graphs import SmartScraperMultiGraph

load_dotenv()

# ************************************************
# Define the configuration for the graph
# ************************************************

graph_config = {  
    "llm": {
        "model": "ernie/ernie-bot-turbo",
        "ernie_client_id": "<ernie_client_id>",
        "ernie_client_secret": "<ernie_client_secret>",
        "temperature": 0.1
    },
    "verbose": True,
    "headless": False,
}

# *******************************************************
# Create the SmartScraperMultiGraph instance and run it
# *******************************************************

multiple_search_graph = SmartScraperMultiGraph(
    prompt="Who is Marco Perini?",
    source= [
        "https://perinim.github.io/",
        "https://perinim.github.io/cv/"
        ],
    schema=None,
    config=graph_config
)

result = multiple_search_graph.run()
print(json.dumps(result, indent=4))
