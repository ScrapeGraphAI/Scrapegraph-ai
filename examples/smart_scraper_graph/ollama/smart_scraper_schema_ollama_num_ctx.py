"""
SmartScraper with a schema on a local Ollama model, with a larger context window.

Ollama runs models with a small context window by default, so a whole web page
gets truncated and the model's JSON answer can come back cut off. Setting
``num_ctx`` (and keeping ``model_tokens`` in line with it) fixes this.
Runs fully locally with no API keys:

    ollama pull llama3.2:3b
"""

import json

from pydantic import BaseModel, Field

from scrapegraphai.graphs import SmartScraperGraph
from scrapegraphai.utils import prettify_exec_info


# ************************************************
# Define the output schema
# ************************************************
class Book(BaseModel):
    title: str = Field(description="The title of the book")
    price: str = Field(description="The price of the book, including currency")


class Books(BaseModel):
    books: list[Book]


# ************************************************
# Define the configuration for the graph
# ************************************************

graph_config = {
    "llm": {
        "model": "ollama/llama3.2:3b",
        "temperature": 0,
        "format": "json",
        "base_url": "http://localhost:11434",
        "model_tokens": 8192,
        # Ollama's context window; without it the page is truncated
        "num_ctx": 8192,
    },
    "verbose": True,
    "headless": True,
}

# ************************************************
# Create the SmartScraperGraph instance and run it
# ************************************************

smart_scraper_graph = SmartScraperGraph(
    prompt="List every book on the page with its title and price.",
    source="https://books.toscrape.com/",
    schema=Books,
    config=graph_config,
)

result = smart_scraper_graph.run()
print(json.dumps(result, indent=4))

# ************************************************
# Get graph execution info
# ************************************************

graph_exec_info = smart_scraper_graph.get_execution_info()
print(prettify_exec_info(graph_exec_info))
