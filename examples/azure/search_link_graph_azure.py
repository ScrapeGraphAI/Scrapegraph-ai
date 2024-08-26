"""
Example of Search Link Graph
"""
import os
from dotenv import load_dotenv
from scrapegraphai.graphs import SearchLinkGraph
from scrapegraphai.utils import convert_to_csv, convert_to_json, prettify_exec_info

# ************************************************
# Define the configuration for the graph
# ************************************************

load_dotenv()

graph_config = {
    "llm": {
        "api_key": os.environ["AZURE_OPENAI_KEY"],
        "model": "azure_openai/gpt-3.5-turbo",
    },
    "verbose": True,
    "headless": False
}

# ************************************************
# Create the SearchLinkGraph instance and run it
# ************************************************

search_link_graph = SearchLinkGraph(
    prompt="List me the best escursions near Trento",
    config=graph_config
)

result = search_link_graph.run()
print(result)

# ************************************************
# Get graph execution info
# ************************************************

graph_exec_info = search_link_graph.get_execution_info()
print(prettify_exec_info(graph_exec_info))

# Save to json and csv
convert_to_csv(result, "result")
convert_to_json(result, "result")
