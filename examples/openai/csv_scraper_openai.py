"""
Basic example of scraping pipeline using CsvScraperGraph from CSV documents
"""

import os
from dotenv import load_dotenv
import pandas as pd
from scrapegraphai.graphs import CsvScraperGraph
from scrapegraphai.utils import convert_to_csv, convert_to_json, prettify_exec_info

load_dotenv()
# ************************************************
# Read the csv file
# ************************************************

text = pd.read_csv("inputs/username.csv")

# ************************************************
# Define the configuration for the graph
# ************************************************

openai_key = os.getenv("OPENAI_APIKEY")

graph_config = {
    "llm": {
        "api_key": openai_key,
        "model": "gpt-3.5-turbo",
    },
}

# ************************************************
# Create the CsvScraperGraph instance and run it
# ************************************************

csv_scraper_graph = CsvScraperGraph(
    prompt="List me all the last names",
    source=str(text),  # Pass the content of the file, not the file object
    config=graph_config
)

result = csv_scraper_graph.run()
print(result)

# ************************************************
# Get graph execution info
# ************************************************

graph_exec_info = csv_scraper_graph.get_execution_info()
print(prettify_exec_info(graph_exec_info))

# Save to json or csv
convert_to_csv(result, "result")
convert_to_json(result, "result")
