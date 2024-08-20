"""
Basic example of scraping pipeline using CSVScraperGraph from CSV documents
"""

import os
from dotenv import load_dotenv
import pandas as pd
from scrapegraphai.graphs import CSVScraperGraph
from scrapegraphai.utils import convert_to_csv, convert_to_json, prettify_exec_info

load_dotenv()

# ************************************************
# Read the csv file
# ************************************************

text = pd.read_csv("inputs/username.csv")

# ************************************************
# Define the configuration for the graph
# ************************************************
gemini_key = os.getenv("GOOGLE_APIKEY")

graph_config = {
    "llm": {
        "api_key": gemini_key,
        "model": "google_genai/gemini-pro",
    },
}

# ************************************************
# Create the CSVScraperGraph instance and run it
# ************************************************

csv_scraper_graph = CSVScraperGraph(
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
