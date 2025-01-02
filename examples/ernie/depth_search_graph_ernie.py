"""
depth_search_graph_opeani example
"""
from scrapegraphai.graphs import DepthSearchGraph

graph_config = {
    "llm": {
        "model": "ernie/ernie-bot-turbo",
        "ernie_client_id": "<ernie_client_id>",
        "ernie_client_secret": "<ernie_client_secret>",
        "temperature": 0.1
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
