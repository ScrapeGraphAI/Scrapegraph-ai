""" 
Basic example of scraping pipeline using SmartScraper
"""
from scrapegraphai.graphs import SmartScraperGraph

# ************************************************
# Define the configuration for the graph
# ************************************************


graph_config = {
    "llm": {
        "model": "ollama/mistral",
        "temperature": 0,
        "format": "json",  # Ollama needs the format to be specified explicitly
    },
}

# ************************************************
# Create the SmartScraperGraph instance and run it
# ************************************************

smart_scraper_graph = SmartScraperGraph(
    prompt="List me all the news with their description.",
    # also accepts a string with the already downloaded HTML code
    source="https://www.wired.com",
    config=graph_config
)

result = smart_scraper_graph.run()
print(result)
