"""
Basic example of scraping pipeline using ScriptCreatorGraph
"""
from scrapegraphai.graphs import ScriptCreatorGraph
from scrapegraphai.utils import prettify_exec_info
# ************************************************
# Define the configuration for the graph
# ************************************************

graph_config = {
    "llm": {
        "model": "ollama/llama3.1",
        "temperature": 0.5,
        # "model_tokens": 2000, # set context length arbitrarily,
        "base_url": "http://localhost:11434",  # set ollama URL arbitrarily
    },
    "library": "beautifoulsoup",
    "verbose": True,
}

# ************************************************
# Create the ScriptCreatorGraph instance and run it
# ************************************************

smart_scraper_graph = ScriptCreatorGraph(
    prompt="List me all the news with their description.",
    # also accepts a string with the already downloaded HTML code
    source="https://perinim.github.io/projects",
    config=graph_config
)

result = smart_scraper_graph.run()
print(result)

# ************************************************
# Get graph execution info
# ************************************************

graph_exec_info = smart_scraper_graph.get_execution_info()
print(prettify_exec_info(graph_exec_info))
