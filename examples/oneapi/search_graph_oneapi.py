"""
Example of Search Graph
"""
from scrapegraphai.graphs import SearchGraph

# ************************************************
# Define the configuration for the graph
# ************************************************

graph_config = {
    "llm": {
        "api_key": "***************************",
        "model": "oneapi/qwen-turbo",
        "base_url": "http://127.0.0.1:3000/v1",  # 设置 OneAPI URL
    }
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
