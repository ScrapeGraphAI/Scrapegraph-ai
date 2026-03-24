"""
Example of Search Graph
"""

import os

from dotenv import load_dotenv

from scrapegraphai.graphs import SearchGraph

load_dotenv()

# ************************************************
# Define the configuration for the graph
# ************************************************

openai_key = os.getenv("OPENAI_API_KEY")

graph_config = {
    "llm": {
        "api_key": openai_key,
        "model": "openai/gpt-4o",
    },
    "max_results": 2,
    "verbose": True,
}

# ************************************************
# Alternative: Use Tavily as the search engine
# Uncomment the block below and set TAVILY_API_KEY
# in your .env file to use Tavily instead.
# ************************************************

# tavily_key = os.getenv("TAVILY_API_KEY")
#
# graph_config = {
#     "llm": {
#         "api_key": openai_key,
#         "model": "openai/gpt-4o",
#     },
#     "search_engine": "tavily",
#     "tavily_api_key": tavily_key,
#     "max_results": 2,
#     "verbose": True,
# }

# ************************************************
# Create the SearchGraph instance and run it
# ************************************************

search_graph = SearchGraph(
    prompt="List me Chioggia's famous dishes", config=graph_config
)

result = search_graph.run()
print(result)
