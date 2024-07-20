"""
Example of Search Graph
"""

import os
from dotenv import load_dotenv
from scrapegraphai.graphs import SearchGraph

load_dotenv()

# ************************************************
# Define the configuration for the graph
# ************************************************

graph_config = {
    "llm": {
            "model": "ernie-bot-turbo",
            "ernie_client_id": "<ernie_client_id>",
            "ernie_client_secret": "<ernie_client_secret>",
            "temperature": 0.1
        },
        "embeddings": {
            "model": "ollama/nomic-embed-text",
            "temperature": 0,
            "base_url": "http://localhost:11434"},
    "library": "beautifulsoup"
}

# ************************************************
# Create the SearchGraph instance and run it
# ************************************************

search_graph = SearchGraph(
    prompt="List me Chioggia's famous dishes",
    config=graph_config
)

result = search_graph.run()
print(result)
