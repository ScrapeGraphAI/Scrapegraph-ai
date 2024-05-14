"""
Example of ImageToTextNode
"""

import os
from dotenv import load_dotenv
from scrapegraphai.nodes import ImageToTextNode
from scrapegraphai.models import OpenAIImageToText

load_dotenv()

# ************************************************
# Define the configuration for the graph
# ************************************************

openai_key = os.getenv("OPENAI_APIKEY")

graph_config = {
    "llm": {
        "api_key": openai_key,
        "model": "gpt-4o",
        "temperature": 0,
    },
}

# ************************************************
# Define the node
# ************************************************

llm_model = OpenAIImageToText(graph_config["llm"])

image_to_text_node = ImageToTextNode(
    input="img_url",
    output=["img_desc"],
    node_config={
        "llm_model": llm_model,
        "headless": False
    }
)

# ************************************************
# Test the node
# ************************************************

state = {
    "img_url": "https://github.com/VinciGit00/Scrapegraph-ai/blob/main/docs/assets/scrapegraphai_logo.png?raw=true"
}

result = image_to_text_node.execute(state)

print(result)
