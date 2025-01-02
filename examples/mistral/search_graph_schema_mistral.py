"""
Example of Search Graph
"""
import os
from typing import List
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from scrapegraphai.graphs import SearchGraph
from scrapegraphai.utils import convert_to_csv, convert_to_json, prettify_exec_info

load_dotenv()

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

mistral_key = os.getenv("MISTRAL_API_KEY")

graph_config = {
    "llm": {
        "api_key": mistral_key,
        "model": "mistralai/open-mistral-nemo",
    },
    "max_results": 2,
    "verbose": True,
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

# ************************************************
# Get graph execution info
# ************************************************

graph_exec_info = search_graph.get_execution_info()
print(prettify_exec_info(graph_exec_info))

# Save to json and csv
convert_to_csv(result, "result")
convert_to_json(result, "result")
