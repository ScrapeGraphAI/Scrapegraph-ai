""" 
Basic example of scraping pipeline using ScriptCreatorGraph
"""

import os
from dotenv import load_dotenv
from scrapegraphai.graphs import ScriptCreatorMultiGraph
from scrapegraphai.utils import prettify_exec_info

load_dotenv()

# ************************************************
# Define the configuration for the graph
# ************************************************

mistral_key = os.getenv("MISTRAL_API_KEY")

graph_config = {
    "llm": {
        "api_key": mistral_key,
        "model": "mistralai/open-mistral-nemo",
    },
    "library": "beautifulsoup",
    "verbose": True,
}

# ************************************************
# Create the ScriptCreatorGraph instance and run it
# ************************************************

urls=[
    "https://perinim.github.io/",
    "https://perinim.github.io/cv/"
]

# ************************************************
# Create the ScriptCreatorGraph instance and run it
# ************************************************

script_creator_graph = ScriptCreatorMultiGraph(
    prompt="Who is Marco Perini?",
    source=urls,
    config=graph_config
)

result = script_creator_graph.run()
print(result)

# ************************************************
# Get graph execution info
# ************************************************

graph_exec_info = script_creator_graph.get_execution_info()
print(prettify_exec_info(graph_exec_info))
