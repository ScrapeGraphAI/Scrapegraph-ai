"""
Example of Search Graph
"""
import os
from dotenv import load_dotenv
from scrapegraphai.graphs import SearchGraph
from scrapegraphai.utils import convert_to_csv, convert_to_json, prettify_exec_info

# ************************************************
# Define the configuration for the graph
# ************************************************

load_dotenv()

together_key = os.getenv("TOGETHER_APIKEY")

graph_config = {
    "llm": {
        "model": "togetherai/meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        "api_key": together_key,
    },
    "verbose": True,
}

# ************************************************
# Create the SearchGraph instance and run it
# ************************************************

search_graph = SearchGraph(
    prompt="List me the best escursions near Trento",
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
