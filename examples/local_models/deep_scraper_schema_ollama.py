""" 
Basic example of scraping pipeline using Deep Scraper Graph
"""

import json
from typing import List
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from scrapegraphai.graphs import DeepScraperGraph
from scrapegraphai.utils import prettify_exec_info

load_dotenv()

# ************************************************
# Define the output schema for the graph
# ************************************************
class Product(BaseModel):
    Name: str = Field(description="The name of the product")
    description: str = Field(description="The description of the product if exists")

class Products(BaseModel):
    products: List[Product]

# ************************************************
# Define the configuration for the graph
# ************************************************

graph_config = {
    "llm": {
        "model": "ollama/llama3.1:8b",
        "temperature": 0,
        "format": "json",  # Ollama needs the format to be specified explicitly
        # "model_tokens": 2000, # set context length arbitrarily
        "base_url": "http://localhost:11434",
    },
    "verbose": True,
    "max_depth": 1,
    "filter_config": {
        "diff_domain_filter": True,
        "img_exts": ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico'],
        "lang_indicators": ['lang=', '/fr', '/pt', '/es', '/de', '/jp', '/it'],
        "irrelevant_keywords": [
                '/login', '/signup', '/register', '/contact', 'facebook.com', 'twitter.com', 
                'linkedin.com', 'instagram.com', '.js', '.css', '/wp-content/', '/wp-admin/', 
                '/wp-includes/', '/wp-json/', '/wp-comments-post.php', ';amp', '/about', 
                '/careers', '/jobs', '/privacy', '/terms', '/legal', '/faq', '/help',
                '.pdf', '.zip', '/news', '/files', '/downloads', '/feed', '#breadcrumb'
            ]
    },
}

# ************************************************
# Create the DeepScraperGraph instance and run it
# ************************************************

deep_scraper_graph = DeepScraperGraph(
    prompt="List me all the product with their description.",
    # also accepts a string with the already downloaded HTML code
    source="https://www.waclighting.com/product-category/track-2/track-heads/",
    config=graph_config,
    schema=Products
)

result = deep_scraper_graph.run()
print(json.dumps(result, indent=4))

# ************************************************
# Get graph execution info
# ************************************************

graph_exec_info = deep_scraper_graph.get_execution_info()
print(deep_scraper_graph.get_state("relevant_links"))
print(prettify_exec_info(graph_exec_info))