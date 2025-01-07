""" 
Basic example of scraping pipeline using SmartScraper with schema
"""
import json
from typing import List
from pydantic import BaseModel, Field
from scrapegraphai.graphs import SmartScraperGraph
from scrapegraphai.utils import prettify_exec_info

# ************************************************
# Define the configuration for the graph
# ************************************************
class Project(BaseModel):
    title: str = Field(description="The title of the project")
    description: str = Field(description="The description of the project")

class Projects(BaseModel):
    projects: List[Project]

graph_config = {
    "llm": {
        "model": "ollama/llama3.1",
        "temperature": 0,
        "format": "json",  # Ollama needs the format to be specified explicitly
        # "base_url": "http://localhost:11434", # set ollama URL arbitrarily
    },
    "verbose": True,
    "headless": False
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
print(json.dumps(result, indent=4))
