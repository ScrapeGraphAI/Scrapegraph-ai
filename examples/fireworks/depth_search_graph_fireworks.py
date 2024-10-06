"""
depth_search_graph_opeani example
"""
import os
from dotenv import load_dotenv
from scrapegraphai.graphs import DepthSearchGraph

load_dotenv()

fireworks_api_key = os.getenv("FIREWORKS_APIKEY")

graph_config = {
    "llm": {
        "api_key": fireworks_api_key,
        "model": "fireworks/accounts/fireworks/models/mixtral-8x7b-instruct"
    },
    "verbose": True,
    "headless": False,
    "depth": 2,
    "only_inside_links": False,
}

search_graph = DepthSearchGraph(
    prompt="List me all the projects with their description",
    source="https://perinim.github.io",
    config=graph_config
)

result = search_graph.run()
print(result)
