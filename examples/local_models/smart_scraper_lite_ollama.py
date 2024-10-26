""" 
Basic example of scraping pipeline using SmartScraper

"""
import json
from scrapegraphai.graphs import SmartScraperLiteGraph
from scrapegraphai.utils import prettify_exec_info

graph_config = {
    "llm": {
        "model": "ollama/llama3.1",
        "temperature": 0,
        "format": "json",
        "base_url": "http://localhost:11434",
    },
    "verbose": True,
    "headless": False
}

smart_scraper_lite_graph = SmartScraperLiteGraph(
    prompt="Who is Marco Perini?",
    source="https://perinim.github.io/",
    config=graph_config
)

result = smart_scraper_lite_graph.run()
print(json.dumps(result, indent=4))

graph_exec_info = smart_scraper_lite_graph.get_execution_info()
print(prettify_exec_info(graph_exec_info))
