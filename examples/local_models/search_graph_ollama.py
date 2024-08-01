"""
Example of Search Graph
"""
from scrapegraphai.graphs import SearchGraph
from scrapegraphai.utils import convert_to_csv, convert_to_json, prettify_exec_info

# ************************************************
# Define the configuration for the graph
# ************************************************


graph_config = {
    "llm": {
        "model": "ollama/llama3",
        "temperature": 0,
        # "format": "json",  # Ollama needs the format to be specified explicitly
        # "base_url": "http://localhost:11434",  # set ollama URL arbitrarily
    },
    "max_results": 5,
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
