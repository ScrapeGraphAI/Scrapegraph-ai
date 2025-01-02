"""
Example of custom graph using existing nodes
"""

from langchain_community.chat_models import ChatOllama
from scrapegraphai.nodes import SearchInternetNode

# ************************************************
# Define the configuration for the graph
# ************************************************

graph_config = {
    "llm": {
        "model": "llama3",
        "temperature": 0,
        "streaming": True
    },
    "search_engine": "google",
    "max_results": 3,
    "verbose": True
}

# ************************************************
# Define the node
# ************************************************

llm_model = ChatOllama(graph_config["llm"])

search_node = SearchInternetNode(
    input="user_input",
    output=["search_results"],
    node_config={
        "llm_model": llm_model,
        "search_engine": graph_config["search_engine"],
        "max_results": graph_config["max_results"],
        "verbose": graph_config["verbose"]
    }
)

# ************************************************
# Test the node
# ************************************************

state = {
    "user_input": "What is the capital of France?"
}

result = search_node.execute(state)

print(result)
