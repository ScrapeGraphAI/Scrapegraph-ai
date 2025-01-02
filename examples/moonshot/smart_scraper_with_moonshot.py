""" 
Basic example of scraping pipeline using SmartScraper and model_instace
"""
import os
import json
from langchain_community.chat_models.moonshot import MoonshotChat
from dotenv import load_dotenv
from scrapegraphai.graphs import SmartScraperGraph
from scrapegraphai.utils import prettify_exec_info

load_dotenv()

# ************************************************
# Define the configuration for the graph
# ************************************************


llm_instance_config = {
    "model": "moonshot-v1-8k",
    "base_url": "https://api.moonshot.cn/v1",
    "moonshot_api_key": os.getenv("MOONLIGHT_API_KEY"),
}


llm_model_instance = MoonshotChat(**llm_instance_config)

graph_config = {
    "llm": {
        "model_instance": llm_model_instance, 
        "model_tokens": 10000
    },
    "verbose": True,
    "headless": True,
}

# ************************************************
# Create the SmartScraperGraph instance and run it
# ************************************************

smart_scraper_graph = SmartScraperGraph(
    prompt="List me what does the company do, the name and a contact email.",
    source="https://scrapegraphai.com/",
    config=graph_config
)

result = smart_scraper_graph.run()
print(json.dumps(result, indent=4))

# ************************************************
# Get graph execution info
# ************************************************

graph_exec_info = smart_scraper_graph.get_execution_info()
print(prettify_exec_info(graph_exec_info))
