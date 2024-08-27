"""
Example of Search Link Graph
"""
from scrapegraphai.graphs import SearchLinkGraph
from scrapegraphai.utils import convert_to_csv, convert_to_json, prettify_exec_info

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
