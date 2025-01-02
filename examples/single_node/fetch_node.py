"""
Example of custom graph using existing nodes
"""

from scrapegraphai.nodes import FetchNode

# ************************************************
# Define the node
# ************************************************


fetch_node = FetchNode(
    input="url | local_dir",
    output=["doc"],
    node_config={
        "headless": False
    }
)

# ************************************************
# Test the node
# ************************************************

state = {
    "url": "https://twitter.com/home"
}

result = fetch_node.execute(state)

print(result)
