""" 
Basic example of scraping pipeline using SmartScraper with schema
"""

import os, json
from typing import List
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from scrapegraphai.graphs import SmartScraperGraph

load_dotenv()

# ************************************************
# Define the output schema for the graph
# ************************************************

class Project(BaseModel):
    title: str = Field(description="The title of the project")
    description: str = Field(description="The description of the project")

class Projects(BaseModel):
    projects: List[Project]

# ************************************************
# Define the configuration for the graph
# ************************************************

nemotron_key = os.getenv("NEMOTRON_APIKEY")

graph_config = {
    "llm": {
        "api_key":nemotron_key,
        "model": "nvidia/meta/llama3-70b-instruct",
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
    config=graph_config
)

result = smart_scraper_graph.run()
print(result)
