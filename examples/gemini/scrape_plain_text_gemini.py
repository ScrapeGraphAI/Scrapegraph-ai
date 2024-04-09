""" 
Basic example of scraping pipeline using SmartScraper from text
"""

import os
from dotenv import load_dotenv
from scrapegraphai.graphs import SmartScraperGraph
from scrapegraphai.utils import convert_to_csv, convert_to_json
load_dotenv()

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

gemini_key = os.getenv("GOOGLE_APIKEY")

graph_config = {
    "llm": {
        "api_key": gemini_key,
        "model": "gemini-pro",
        "temperature": 0,
        "streaming": True
    },
}

# ************************************************
# Create the SmartScraperGraph instance and run it
# ************************************************

smart_scraper_graph = SmartScraperGraph(
    prompt="List me all the news with their description.",
    source=text,
    config=graph_config
)

result = smart_scraper_graph.run()
print(result)

# Save to json or csv
convert_to_csv(result, "result")
convert_to_json(result, "result")
