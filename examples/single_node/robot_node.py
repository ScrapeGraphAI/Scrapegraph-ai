"""
Example of custom graph using existing nodes
"""

from scrapegraphai.models import Ollama
from scrapegraphai.nodes import RobotsNode

# ************************************************
# Define the configuration for the graph
# ************************************************

graph_config = {
    "llm": {
        "model": "ollama/llama3",
        "temperature": 0,
        "streaming": True
    },
     "embeddings": {
        "model": "ollama/nomic-embed-text",
        "temperature": 0,
        # "base_url": "http://localhost:11434",  # set ollama URL arbitrarily
    }
}

# ************************************************
# Define the node
# ************************************************

llm_model = Ollama(graph_config["llm"])

robots_node = RobotsNode(
    input="url",
    output=["is_scrapable"],
    node_config={"llm_model": llm_model,
                 "headless": False
                 }
)

# ************************************************
# Test the node
# ************************************************

state = {
    "url": "https://twitter.com/home"
}

result = robots_node.execute(state)

print(result)
