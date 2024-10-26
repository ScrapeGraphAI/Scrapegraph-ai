"""
Basic example of scraping pipeline using SmartScraperMultiConcatGraph with Groq
"""

import os
import json
from dotenv import load_dotenv
from scrapegraphai.graphs import SmartScraperGraph

load_dotenv()

# ************************************************
# Define the configuration for the graph
# ************************************************

graph_config = {
    "llm": {
        "api_key": os.getenv("GROQ_APIKEY"),
        "model": "groq/gemma-7b-it",
    },
    "verbose": True,
    "headless": True,
    "reattempt": True #Setting this to True will allow the graph to reattempt the scraping process
}

# *******************************************************
# Create the SmartScraperMultiCondGraph instance and run it
# *******************************************************

multiple_search_graph = SmartScraperGraph(
    prompt="Who is Marco Perini?",
    source="https://perinim.github.io/",
    schema=None,
    config=graph_config
)

result = multiple_search_graph.run()
print(json.dumps(result, indent=4))
