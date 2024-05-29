""" 
Basic example of scraping pipeline using SmartScraper using Azure OpenAI Key
"""

import os
from dotenv import load_dotenv
from scrapegraphai.graphs import SmartScraperGraph
from scrapegraphai.utils import prettify_exec_info


# required environment variables in .env
# HUGGINGFACEHUB_API_TOKEN
# ANTHROPIC_API_KEY
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
# Create the SmartScraperGraph instance and run it
# ************************************************

graph_config = {
    "llm": {
        "api_key": os.getenv("ANTHROPIC_API_KEY"),
        "model": "claude-3-haiku-20240307",
        "max_tokens": 4000},
}

smart_scraper_graph = SmartScraperGraph(
    prompt="List me all the projects with their description",
    # also accepts a string with the already downloaded HTML code
    schema=schema,
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
