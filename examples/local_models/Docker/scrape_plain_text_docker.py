""" 
Basic example of scraping pipeline using SmartScraper from text
"""

import os
from scrapegraphai.graphs import SmartScraperGraph
from scrapegraphai.utils import convert_to_csv, convert_to_json

# ************************************************
# Read the text file
# ************************************************

FILE_NAME = "inputs/plain_html_example.txt"
curr_dir = os.path.dirname(os.path.realpath(__file__))
file_path = os.path.join(curr_dir, FILE_NAME)

# It could be also a http request using the request model
with open(file_path, 'r', encoding="utf-8") as file:
    text = file.read()

# ************************************************
# Define the configuration for the graph
# ************************************************

graph_config = {
    "llm": {
        "model": "ollama/mistral",
        "temperature": 0,
        "format": "json",  # Ollama needs the format to be specified explicitly
        # "model_tokens": 2000, # set context length arbitrarily
    },
    "embeddings": {
        "model": "ollama/nomic-embed-text",
        "temperature": 0,
    }
}

# ************************************************
# Create the SmartScraperGraph instance and run it
# ************************************************

smart_scraper_graph = SmartScraperGraph(
    prompt="List me all the projects with their description.",
    source=text,
    config=graph_config
)

result = smart_scraper_graph.run()
print(result)

# Save to json or csv
convert_to_csv(result, "result")
convert_to_json(result, "result")
