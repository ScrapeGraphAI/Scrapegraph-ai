""" 
Basic example of scraping pipeline using ScriptCreatorGraph
"""

import os
from dotenv import load_dotenv
from scrapegraphai.graphs import ScriptCreatorGraph
from scrapegraphai.utils import prettify_exec_info

load_dotenv()

# ************************************************
# Define the configuration for the graph
# ************************************************

deepseek_key = os.getenv("DEEPSEEK_APIKEY")

graph_config = {
    "llm": {
        "model": "deepseek/deepseek-chat",
        "api_key": deepseek_key, 
    },
    "library": "beautifulsoup"
}

# ************************************************
# Create the ScriptCreatorGraph instance and run it
# ************************************************

script_creator_graph = ScriptCreatorGraph(
    prompt="List me all the projects with their description.",
    # also accepts a string with the already downloaded HTML code
    source="https://perinim.github.io/projects",
    config=graph_config
)

result = script_creator_graph.run()
print(result)

# ************************************************
# Get graph execution info
# ************************************************

graph_exec_info = script_creator_graph.get_execution_info()
print(prettify_exec_info(graph_exec_info))
