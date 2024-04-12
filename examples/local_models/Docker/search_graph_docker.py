"""
Example of Search Graph
"""

from scrapegraphai.graphs import SearchGraph
from scrapegraphai.utils import convert_to_csv, convert_to_json

# ************************************************
# Define the configuration for the graph
# ************************************************


graph_config = {
    "llm": {
        "model": "ollama/mistral",
        "temperature": 0,
        "format": "json",  # Ollama needs the format to be specified explicitly
        # "model_tokens": 2000, # set context length arbitrarily
    },
    "embeddings": {
        "model": "ollama/nomic-embed-text",
        "temperature": 0,
    }
}

# ************************************************
# Create the SearchGraph instance and run it
# ************************************************

search_graph = SearchGraph(
    prompt="List me all the regions of Italy.",
    config=graph_config
)

result = search_graph.run()
print(result)

# Save to json and csv
convert_to_csv(result, "result")
convert_to_json(result, "result")
