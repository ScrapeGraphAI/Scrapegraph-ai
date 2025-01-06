"""
Basic example of scraping pipeline using CSVScraperGraph from CSV documents
"""
import os
from dotenv import load_dotenv
from scrapegraphai.graphs import CSVScraperGraph
from scrapegraphai.utils import prettify_exec_info

load_dotenv()

# ************************************************
# Read the CSV file
# ************************************************

FILE_NAME = "inputs/username.csv"
curr_dir = os.path.dirname(os.path.realpath(__file__))
file_path = os.path.join(curr_dir, FILE_NAME)

with open(file_path, 'r') as file:
    text = file.read()

# ************************************************
# Define the configuration for the graph
# ************************************************

# required environment variables in .env
# HUGGINGFACEHUB_API_TOKEN
# ANTHROPIC_API_KEY
load_dotenv()

graph_config = {
    "llm": {
        "api_key": os.getenv("ANTHROPIC_API_KEY"),
        "model": "anthropic/claude-3-haiku-20240307",
    },
}

# ************************************************
# Create the CSVScraperGraph instance and run it
# ************************************************

csv_scraper_graph = CSVScraperGraph(
    prompt="List me all the last names",
    source=text,  # Pass the content of the file
    config=graph_config
)

result = csv_scraper_graph.run()
print(result)

# ************************************************
# Get graph execution info
# ************************************************

graph_exec_info = csv_scraper_graph.get_execution_info()
print(prettify_exec_info(graph_exec_info))