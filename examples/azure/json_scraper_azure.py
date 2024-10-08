""" 
Basic example of scraping pipeline using SmartScraper using Azure OpenAI Key
"""
import os
from dotenv import load_dotenv
from scrapegraphai.graphs import JSONScraperGraph
from scrapegraphai.utils import prettify_exec_info

load_dotenv()

FILE_NAME = "inputs/example.json"
curr_dir = os.path.dirname(os.path.realpath(__file__))
file_path = os.path.join(curr_dir, FILE_NAME)

with open(file_path, 'r', encoding="utf-8") as file:
    text = file.read()

# ************************************************
# Initialize the model instances
# ************************************************

graph_config = {
    "llm": {
        "api_key": os.environ["AZURE_OPENAI_KEY"],
        "model": "azure_openai/gpt-4o"
    },
    "verbose": True,
    "headless": False
}

smart_scraper_graph = JSONScraperGraph(
    prompt="List me all the authors, title and genres of the books",
    source=text,  # Pass the content of the file, not the file object
    config=graph_config
)

result = smart_scraper_graph.run()
print(result)

# ************************************************
# Get graph execution info
# ************************************************

graph_exec_info = smart_scraper_graph.get_execution_info()
print(prettify_exec_info(graph_exec_info))
