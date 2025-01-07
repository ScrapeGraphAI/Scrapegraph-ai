"""
Basic example of scraping pipeline using DocumentScraperGraph from MD documents
"""
import os
from dotenv import load_dotenv
from scrapegraphai.graphs import DocumentScraperGraph
from scrapegraphai.utils import convert_to_csv, convert_to_json, prettify_exec_info

load_dotenv()

# ************************************************
# Read the MD file
# ************************************************

FILE_NAME = "inputs/markdown_example.md"
curr_dir = os.path.dirname(os.path.realpath(__file__))
file_path = os.path.join(curr_dir, FILE_NAME)

with open(file_path, 'r', encoding="utf-8") as file:
    text = file.read()

# ************************************************
# Define the configuration for the graph
# ************************************************

openai_key = os.getenv("OPENAI_APIKEY")

graph_config = {
    "llm": {
        "api_key": openai_key,
        "model": "openai/gpt-4o",
    },
}

# ************************************************
# Create the DocumentScraperGraph instance and run it
# ************************************************

md_scraper_graph = DocumentScraperGraph(
    prompt="List me all the projects",
    source=text,  # Pass the content of the file, not the file object
    config=graph_config
)

result = md_scraper_graph.run()
print(result)

# ************************************************
# Get graph execution info
# ************************************************

graph_exec_info = md_scraper_graph.get_execution_info()
print(prettify_exec_info(graph_exec_info))

# Save to json or csv
convert_to_csv(result, "result")
convert_to_json(result, "result")
