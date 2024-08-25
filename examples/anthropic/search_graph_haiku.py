"""
Example of Search Graph
"""

import os
from dotenv import load_dotenv
from scrapegraphai.graphs import SearchGraph
from scrapegraphai.utils import convert_to_csv, convert_to_json, prettify_exec_info
load_dotenv()

# ************************************************
# Define the configuration for the graph
# ************************************************

graph_config = {
    "llm": {
        "api_key": os.getenv("ANTHROPIC_API_KEY"),
        "model": "claude-3-haiku-20240307",
        "max_tokens": 4000
        },
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

# ************************************************
# Get graph execution info
# ************************************************

graph_exec_info = search_graph.get_execution_info()
print(prettify_exec_info(graph_exec_info))

# Save to json and csv
convert_to_csv(result, "result")
convert_to_json(result, "result")
