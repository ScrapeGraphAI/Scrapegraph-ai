"""
depth_search_graph_opeani example
"""
import os
from dotenv import load_dotenv
from scrapegraphai.graphs import DepthSearchGraph

load_dotenv()

openai_key = os.getenv("OPENAI_APIKEY")

graph_config = {
   "llm": {
        "api_key": os.environ["AZURE_OPENAI_KEY"],
        "model": "azure_openai/gpt-4o",
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
