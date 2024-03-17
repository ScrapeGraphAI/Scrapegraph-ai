""" 
Basic example of scraping pipeline using SmartScraper
"""

import os
from dotenv import load_dotenv
from scrapegraphai.graphs import SmartScraperGraph

load_dotenv()
openai_key = os.getenv("OPENAI_APIKEY")

# Define the configuration for the graph
graph_config = {
    "llm": {
        "api_key": openai_key,
        "model": "gpt-3.5-turbo",
    },
    # "embedding_model": {
    #     "api_key": openai_key,
    #     "model": "gpt-3.5-turbo",
    # },
}

# Create the SmartScraperGraph instance
smart_scraper_graph = SmartScraperGraph(
    prompt = "List me all the news with their description.",
    url = "https://www.ansa.it/veneto/",
    config = graph_config
)

answer = smart_scraper_graph.run()
print(answer)
