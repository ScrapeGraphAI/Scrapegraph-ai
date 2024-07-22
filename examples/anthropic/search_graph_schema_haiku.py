"""
Example of Search Graph
"""

import os
from dotenv import load_dotenv
load_dotenv()

from scrapegraphai.graphs import SearchGraph

from pydantic import BaseModel, Field
from typing import List

# ************************************************
# Define the output schema for the graph
# ************************************************

class Dish(BaseModel):
    name: str = Field(description="The name of the dish")
    description: str = Field(description="The description of the dish")

class Dishes(BaseModel):
    dishes: List[Dish]

# ************************************************
# Define the configuration for the graph
# ************************************************
graph_config = {
    "llm": {
        "api_key": os.getenv("ANTHROPIC_API_KEY"),
        "model": "claude-3-haiku-20240307",
        "max_tokens": 4000},
}

# ************************************************
# Create the SearchGraph instance and run it
# ************************************************

search_graph = SearchGraph(
    prompt="List me Chioggia's famous dishes",
    config=graph_config,
    schema=Dishes
)

result = search_graph.run()
print(result)
