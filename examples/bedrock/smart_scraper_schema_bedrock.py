""" 
Basic example of scraping pipeline using SmartScraper
"""

import os
from dotenv import load_dotenv
from scrapegraphai.graphs import SmartScraperGraph
from scrapegraphai.utils import prettify_exec_info

load_dotenv()
# ************************************************
# Define the output schema for the graph
# ************************************************

schema= """
    { 
    "Projects": [
        "Project #": 
            { 
                "title": "...", 
                "description": "...", 
            }, 
        "Project #": 
            { 
                "title": "...", 
                "description": "...", 
            } 
        ] 
    } 
"""

# ************************************************
# Define the configuration for the graph
# ************************************************

graph_config = {
    "llm": {
        "client": "client_name",
        "model": "bedrock/anthropic.claude-3-sonnet-20240229-v1:0",
        "temperature": 0.0
    },
    "embeddings": {
        "model": "bedrock/cohere.embed-multilingual-v3"
    }
}

# ************************************************
# Create the SmartScraperGraph instance and run it
# ************************************************

smart_scraper_graph = SmartScraperGraph(
    prompt="List me all the projects with their description",
    # also accepts a string with the already downloaded HTML code
    source="https://perinim.github.io/projects/",
    schema=schema,
    config=graph_config
)

result = smart_scraper_graph.run()
print(result)

# ************************************************
# Get graph execution info
# ************************************************

graph_exec_info = smart_scraper_graph.get_execution_info()
print(prettify_exec_info(graph_exec_info))
