"""Free, local ScrapeGraphAI example: SmartScraperGraph + Ollama (no API keys)."""
import json

from pydantic import BaseModel

from scrapegraphai.graphs import SmartScraperGraph

class Book(BaseModel):
    title: str
    price: str


class Books(BaseModel):
    books: list[Book]


graph_config = {
    "llm": {
        "model": "ollama/llama3.2:3b",
        "base_url": "http://127.0.0.1:11434",
        "temperature": 0,
        "format": "json",
        "model_tokens": 8192,
        "num_ctx": 8192,
    },
    "headless": True,
    "verbose": False,
}

graph = SmartScraperGraph(
    prompt="List every book on the page with its title and price.",
    source="https://books.toscrape.com/",
    config=graph_config,
    schema=Books,
)

print(json.dumps(graph.run(), indent=2))
