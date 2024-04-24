"""
Example of custom graph using existing nodes
"""

import os
from dotenv import load_dotenv
from scrapegraphai.models import OpenAI
from scrapegraphai.nodes import RobotsNode
load_dotenv()

# ************************************************
# Define the configuration for the graph
# ************************************************

openai_key = os.getenv("OPENAI_APIKEY")

graph_config = {
    "llm": {
        "api_key": openai_key,
        "model": "gpt-3.5-turbo",
        "temperature": 0,
        "streaming": True
    },
}

# ************************************************
# Define the node
# ************************************************

llm_model = OpenAI(graph_config["llm"])

robots_node = RobotsNode(
    input="url",
    output=["is_scrapable"],
    node_config={"llm": llm_model}
)

# ************************************************
# Test the node
# ************************************************

state = {
    "url": "https://twitter.com/home"
}

result = robots_node.execute(state)

print(result)
