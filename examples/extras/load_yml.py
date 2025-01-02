""" 
Basic example of scraping pipeline using SmartScraper
"""
import yaml
from scrapegraphai.graphs import SmartScraperGraph
from scrapegraphai.utils import prettify_exec_info

# ************************************************
# Define the configuration for the graph
# ************************************************
with open("example.yml", 'r') as file:
    graph_config = yaml.safe_load(file)

# ************************************************
# Create the SmartScraperGraph instance and run it
# ************************************************

smart_scraper_graph = SmartScraperGraph(
    prompt="List me all the titles",
    source="https://sport.sky.it/nba?gr=www",
    config=graph_config
)

result = smart_scraper_graph.run()
print(result)

# ************************************************
# Get graph execution info
# ************************************************

graph_exec_info = smart_scraper_graph.get_execution_info()
print(prettify_exec_info(graph_exec_info))
