"""
Module for showing how JSONScraperMultiGraph multi works
"""
import os
from dotenv import load_dotenv
import json
from scrapegraphai.graphs import JSONScraperMultiGraph

load_dotenv()


graph_config = {
    "llm": {
        "api_key": os.environ["AZURE_OPENAI_KEY"],
        "model": "azure/gpt-3.5-turbo",
    },
    "verbose": True,
    "headless": False
}

FILE_NAME = "inputs/example.json"
curr_dir = os.path.dirname(os.path.realpath(__file__))
file_path = os.path.join(curr_dir, FILE_NAME)

with open(file_path, 'r', encoding="utf-8") as file:
    text = file.read()

sources = [text, text]

multiple_search_graph = JSONScraperMultiGraph(
    prompt= "List me all the authors, title and genres of the books",
    source= sources,
    schema=None,
    config=graph_config
)

result = multiple_search_graph.run()
print(json.dumps(result, indent=4))
