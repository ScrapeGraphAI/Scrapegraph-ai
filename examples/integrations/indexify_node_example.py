""" 
Basic example of scraping pipeline using SmartScraper with schema
"""

import os, json
from typing import List

from dotenv import load_dotenv
load_dotenv()

from pydantic import BaseModel, Field
from scrapegraphai.graphs import SmartScraperGraph
from scrapegraphai.integrations import IndexifyNode


# ************************************************
# Define the output schema for the graph
# ************************************************

class Image(BaseModel):
    url: str = Field(description="The url of the image")

class Images(BaseModel):
    images: List[Image]

# ************************************************
# Define the configuration for the graph
# ************************************************

openai_key = os.getenv("OPENAI_APIKEY")

graph_config = {
    "llm": {
        "api_key":openai_key,
        "model": "gpt-3.5-turbo",
    },
    "verbose": True,
    "headless": False,
}

# ************************************************
# Define the custom nodes for the graph
# ************************************************

indexify_node = IndexifyNode(
    input="answer & img_urls",
    output=["is_indexed"],
    node_config={
        "verbose": True
    }
)

# ************************************************
# Create the SmartScraperGraph instance
# ************************************************

smart_scraper_graph = SmartScraperGraph(
    prompt="List me all the images with their url",
    source="https://giphy.com/",
    schema=Images,
    config=graph_config
)

# Add the custom node to the graph
smart_scraper_graph.append_node(indexify_node)

# ************************************************
# Run the SmartScraperGraph
# ************************************************

result = smart_scraper_graph.run()
print(json.dumps(result, indent=2))
