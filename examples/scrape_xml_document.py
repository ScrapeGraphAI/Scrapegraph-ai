"""
Basic example of scraping pipeline using SmartScraper from XML documents
"""

import os
from dotenv import load_dotenv
from scrapegraphai.graphs import SmartScraperGraph
from scrapegraphai.utils import convert_to_csv, convert_to_json

load_dotenv()
openai_key = os.getenv("OPENAI_APIKEY")

# Define the configuration for the graph
graph_config = {
    "llm": {
        "api_key": openai_key,
        "model": "gpt-3.5-turbo",
    },
}

# Read the XML file
with open('inputs/books.xml', 'r', encoding="utf-8") as file:
    text = file.read()

# Create the SmartScraperGraph instance
smart_scraper_graph = SmartScraperGraph(
    prompt="List me all the authors, title and genres of the books",
    file_source=text,  # Pass the content of the file, not the file object
    config=graph_config
)

result = smart_scraper_graph.run()
print(result)

# Save to json or csv
convert_to_csv(result, "result")
convert_to_json(result, "result")
