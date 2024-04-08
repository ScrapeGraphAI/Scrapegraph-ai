"""
Example of Search Graph
"""

import os
from dotenv import load_dotenv
from scrapegraphai.graphs import SearchGraph
from scrapegraphai.utils import convert_to_csv, convert_to_json
load_dotenv()

# ************************************************
# Define the configuration for the graph
# ************************************************

openai_key = os.getenv("OPENAI_APIKEY")

graph_config = {
    "llm": {
        "model": "ollama/mistral",
        "temperature": 0,
        "format": "json", # Ollama needs the format to be specified explicitly
    },
    "embeddings": {
        "api_key": openai_key,
        "model": "gpt-3.5-turbo",
    },
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
