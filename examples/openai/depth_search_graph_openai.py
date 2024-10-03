"""
depth_search_graph_opeani example
"""
from scrapegraphai.graphs import DepthSearchGraph

graph_config = {
    "llm": {
        "api_key":"YOUR_API_KEY",
        "model": "openai/gpt-4o-mini",
    },
    "verbose": True,
    "headless": False,
    "depth": 2,
    "only_inside_links": True,
}

search_graph = DepthSearchGraph(
    prompt="List me all the projects with their description",
    source="https://perinim.github.io/projects/",
    config=graph_config
)

result = search_graph.run()
print(result)
