"""
Example of Search Graph
"""

import os
from dotenv import load_dotenv
from scrapegraphai.graphs import SearchGraph

load_dotenv()
openai_key = os.getenv("OPENAI_APIKEY")

# Define the configuration for the graph
graph_config = {
    "llm": {
        "api_key": openai_key,
        "model": "gpt-3.5-turbo",
        "temperature": 0,
    },
}

# Create the SmartScraperGraph instance
smart_scraper_graph = SearchGraph(
    prompt="List me all the regions of Italy.",
    config=graph_config
)

result = smart_scraper_graph.run()
print(result)