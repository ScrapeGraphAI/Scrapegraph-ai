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

deepseek_key = os.getenv("DEEPSEEK_APIKEY")

graph_config = {
    "llm": {
        "model": "deepseek-chat",
        "openai_api_key": deepseek_key,
        "openai_api_base": 'https://api.deepseek.com/v1',
    },
    "verbose": True,
}

# ************************************************
# Create the SearchLinkGraph instance and run it
# ************************************************

search_link_graph = SearchLinkGraph(
    source="https://sport.sky.it/nba?gr=www",
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
