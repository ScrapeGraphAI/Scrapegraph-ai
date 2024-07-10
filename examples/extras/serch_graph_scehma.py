"""
Example of Search Graph
"""

import os
from dotenv import load_dotenv
from scrapegraphai.graphs import SearchGraph
from pydantic import BaseModel, Field
from typing import List
load_dotenv()

# ************************************************
# Define the configuration for the graph
# ************************************************
class CeoName(BaseModel):
    ceo_name: str = Field(description="The name and surname of the ceo")

class Ceos(BaseModel):
    names: List[CeoName]

openai_key = os.getenv("OPENAI_APIKEY")

graph_config = {
    "llm": {
        "api_key": openai_key,
        "model": "gpt-4o",
        },
    "max_results": 2,
    "verbose": True,
}

# ************************************************
# Create the SearchGraph instance and run it
# ************************************************

search_graph = SearchGraph(
    prompt=f"Who is the ceo of Appke?",
    schema = Ceos,
    config=graph_config,
)

result = search_graph.run()
print(result)
