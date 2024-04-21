""" 
Basic example of scraping pipeline using SmartScraper from text
"""

import os
from dotenv import load_dotenv
from scrapegraphai.graphs import ScriptCreatorGraph
from scrapegraphai.utils import prettify_exec_info
load_dotenv()

# ************************************************
# Read the text file
# ************************************************
files = ["inputs/example_1.txt", "inputs/example_2.txt"]
tasks = ["List me all the projects with their description.",
         "List me all the articles with their description."]

# ************************************************
# Define the configuration for the graph
# ************************************************

openai_key = os.getenv("GPT4_KEY")


graph_config = {
    "llm": {
        "model": "ollama/llama3",
        "temperature": 0,
        # "model_tokens": 2000, # set context length arbitrarily,
        "base_url": "http://localhost:11434",  # set ollama URL arbitrarily
    },
    "embeddings": {
        "model": "ollama/nomic-embed-text",
        "temperature": 0,
        "base_url": "http://localhost:11434",  # set ollama URL arbitrarily
    },
    "library": "beautifoulsoup"
}


# ************************************************
# Create the SmartScraperGraph instance and run it
# ************************************************

for i in range(0, 2):
    with open(files[i], 'r', encoding="utf-8") as file:
        text = file.read()

    smart_scraper_graph = ScriptCreatorGraph(
        prompt=tasks[i],
        source=text,
        config=graph_config
    )

    result = smart_scraper_graph.run()
    print(result)
    # ************************************************
    # Get graph execution info
    # ************************************************

    graph_exec_info = smart_scraper_graph.get_execution_info()
    print(prettify_exec_info(graph_exec_info))
