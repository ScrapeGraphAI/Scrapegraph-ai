"""
Example of OmniSearchGraph
"""

import os, json
from dotenv import load_dotenv
from scrapegraphai.graphs import OmniSearchGraph
from scrapegraphai.utils import prettify_exec_info
load_dotenv()

# ************************************************
# Define the configuration for the graph
# ************************************************

openai_key = os.getenv("OPENAI_APIKEY")

graph_config = {
    "llm": {
        "api_key": openai_key,
        "model": "gpt-4o",
    },
    "max_results": 2,
    "max_images": 5,
    "verbose": True,
}

# ************************************************
# Create the OmniSearchGraph instance and run it
# ************************************************

omni_search_graph = OmniSearchGraph(
    prompt="List me all Chioggia's famous dishes and describe their pictures.",
    config=graph_config
)

result = omni_search_graph.run()
print(json.dumps(result, indent=2))

# ************************************************
# Get graph execution info
# ************************************************

graph_exec_info = omni_search_graph.get_execution_info()
print(prettify_exec_info(graph_exec_info))

