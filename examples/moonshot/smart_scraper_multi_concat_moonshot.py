""" 
Basic example of scraping pipeline using SmartScraper
"""
import os
import json
from langchain_community.chat_models.moonshot import MoonshotChat
from dotenv import load_dotenv
from scrapegraphai.graphs import SmartScraperMultiConcatGraph
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


# *******************************************************
# Create the SmartScraperMultiGraph instance and run it
# *******************************************************

multiple_search_graph = SmartScraperMultiConcatGraph(
    prompt="Who is Marco Perini?",
    source= [
        "https://perinim.github.io/",
        "https://perinim.github.io/cv/"
        ],
    schema=None,
    config=graph_config
)

result = multiple_search_graph.run()
print(json.dumps(result, indent=4))
