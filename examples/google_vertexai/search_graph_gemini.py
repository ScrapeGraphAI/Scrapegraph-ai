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

gemini_key = os.getenv("GOOGLE_APIKEY")

graph_config = {
    "llm": {
        "api_key": gemini_key,
        "model": "google_vertexai/gemini-1.5-pro",
        "temperature": 0,
        "streaming": True
    },
    "max_results": 5,
    "verbose": True,
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
