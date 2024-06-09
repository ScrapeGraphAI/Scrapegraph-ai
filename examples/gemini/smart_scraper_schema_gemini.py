""" 
Basic example of scraping pipeline using SmartScraper with schema
"""

import os
from typing import List
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from scrapegraphai.utils import prettify_exec_info
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

gemini_key = os.getenv("GOOGLE_APIKEY")

graph_config = {
    "llm": {
        "api_key": gemini_key,
        "model": "gemini-pro",
    },
}

# ************************************************
# Create the SmartScraperGraph instance and run it
# ************************************************

smart_scraper_graph = SmartScraperGraph(
    prompt="List me all the news with their description.",
    # also accepts a string with the already downloaded HTML code
    source="https://www.wired.com",
    schema=Projects,
    config=graph_config
)

result = smart_scraper_graph.run()
print(result)

# ************************************************
# Get graph execution info
# ************************************************

graph_exec_info = smart_scraper_graph.get_execution_info()
print(prettify_exec_info(graph_exec_info))
```