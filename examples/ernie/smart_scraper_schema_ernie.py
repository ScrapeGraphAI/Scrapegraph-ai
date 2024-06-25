""" 
Basic example of scraping pipeline using SmartScraper with schema
"""

import json
import os
from typing import Dict

from dotenv import load_dotenv
from pydantic import BaseModel

from scrapegraphai.graphs import SmartScraperGraph


load_dotenv()

# ************************************************
# Define the output schema for the graph
# ************************************************


class Project(BaseModel):
    title: str
    description: str


class Projects(BaseModel):
    Projects: Dict[str, Project]


# ************************************************
# Define the configuration for the graph
# ************************************************

openai_key = os.getenv("OPENAI_APIKEY")

graph_config = {
    "llm": {
        "api_key": openai_key,
        "model": "gpt-3.5-turbo",
    },
    "verbose": True,
    "headless": False,
}

# ************************************************
# Create the SmartScraperGraph instance and run it
# ************************************************

smart_scraper_graph = SmartScraperGraph(
    prompt="List me all the projects with their description",
    source="https://perinim.github.io/projects/",
    schema=Projects,
    config=graph_config,
)

result = smart_scraper_graph.run()
print(json.dumps(result, indent=4))
