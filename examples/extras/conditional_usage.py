"""
Basic example of scraping pipeline using SmartScraperMultiConcatGraph with Groq
"""

import os
import json
from dotenv import load_dotenv
from scrapegraphai.graphs import SmartScraperMultiGraph

load_dotenv()

# ************************************************
# Define the configuration for the graph
# ************************************************

graph_config = {
    "llm": {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "model": "openai/gpt-4o",
    },

    "verbose": True,
    "headless": False,
}

# *******************************************************
# Create the SmartScraperMultiCondGraph instance and run it
# *******************************************************

multiple_search_graph = SmartScraperMultiGraph(
    prompt="Who is Marco Perini?",
    source=[
        "https://perinim.github.io/",
        "https://perinim.github.io/cv/"
    ],
    schema=None,
    config=graph_config
)

result = multiple_search_graph.run()
print(json.dumps(result, indent=4))
