"""

Basic example of scraping pipeline using XMLScraperMultiGraph from XML documents
"""
import os
from dotenv import load_dotenv
from scrapegraphai.graphs import XMLScraperMultiGraph
from scrapegraphai.utils import convert_to_csv, convert_to_json, prettify_exec_info

load_dotenv()

# ************************************************
# Read the XML file
# ************************************************

FILE_NAME = "inputs/books.xml"
curr_dir = os.path.dirname(os.path.realpath(__file__))
file_path = os.path.join(curr_dir, FILE_NAME)

with open(file_path, 'r', encoding="utf-8") as file:
    text = file.read()

# ************************************************
# Define the configuration for the graph
# ************************************************


nemotron_key = os.getenv("NEMOTRON_APIKEY")

graph_config = {
    "llm": {
        "api_key":nemotron_key,
        "model": "nvidia/meta/llama3-70b-instruct",
    },
    "verbose": True,
    "headless": False,
}
# ************************************************
# Create the XMLScraperMultiGraph instance and run it
# ************************************************

xml_scraper_graph = XMLScraperMultiGraph(
    prompt="List me all the authors, title and genres of the books",
    source=[text, text],  # Pass the content of the file, not the file object
    config=graph_config
)

result = xml_scraper_graph.run()
print(result)

# ************************************************
# Get graph execution info
# ************************************************

graph_exec_info = xml_scraper_graph.get_execution_info()
print(prettify_exec_info(graph_exec_info))

# Save to json or csv
convert_to_csv(result, "result")
convert_to_json(result, "result")
