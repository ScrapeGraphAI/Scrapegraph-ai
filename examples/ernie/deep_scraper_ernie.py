""" 
Basic example of scraping pipeline using SmartScraper
"""

import os
from dotenv import load_dotenv
from scrapegraphai.graphs import DeepScraperGraph
from scrapegraphai.utils import prettify_exec_info

load_dotenv()


# ************************************************
# Define the configuration for the graph
# ************************************************

openai_key = os.getenv("OPENAI_APIKEY")

graph_config = {
    "llm": {
            "model": "ernie-bot-turbo",
            "ernie_client_id": "<ernie_client_id>",
            "ernie_client_secret": "<ernie_client_secret>",
            "temperature": 0.1
        },
        "embeddings": {
            "model": "ollama/nomic-embed-text",
            "temperature": 0,
            "base_url": "http://localhost:11434"},
    "verbose": True,
    "max_depth": 1
}
  

# ************************************************
# Create the SmartScraperGraph instance and run it
# ************************************************

deep_scraper_graph = DeepScraperGraph(
    prompt="List me all the job titles and detailed job description.",
    # also accepts a string with the already downloaded HTML code
    source="https://www.google.com/about/careers/applications/jobs/results/?location=Bangalore%20India",
    config=graph_config
)

result = deep_scraper_graph.run()
print(result)

# ************************************************
# Get graph execution info
# ************************************************

graph_exec_info = deep_scraper_graph.get_execution_info()
print(deep_scraper_graph.get_state("relevant_links"))
print(prettify_exec_info(graph_exec_info))