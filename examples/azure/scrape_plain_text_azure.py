""" 
Basic example of scraping pipeline using SmartScraper from text
"""

import os
from dotenv import load_dotenv
from scrapegraphai.graphs import SmartScraperGraph
from langchain_openai import AzureChatOpenAI
from langchain_openai import AzureOpenAIEmbeddings
from scrapegraphai.utils import prettify_exec_info

load_dotenv()

# ************************************************
# Read the text file
# ************************************************

FILE_NAME = "inputs/plain_html_example.txt"
curr_dir = os.path.dirname(os.path.realpath(__file__))
file_path = os.path.join(curr_dir, FILE_NAME)

# It could be also a http request using the request model
with open(file_path, 'r', encoding="utf-8") as file:
    text = file.read()

# ************************************************
# Define the configuration for the graph
# ************************************************

llm_model_instance = AzureChatOpenAI(
    openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
    azure_deployment=os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"]
)

embedder_model_instance = AzureOpenAIEmbeddings(
    azure_deployment=os.environ["AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT_NAME"],
    openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
)

# ************************************************
# Create the JSONScraperGraph instance and run it
# ************************************************

graph_config = {
    "llm": {"model_instance": llm_model_instance},
    "embeddings": {"model_instance": embedder_model_instance}
}

# ************************************************
# Create the SmartScraperGraph instance and run it
# ************************************************

smart_scraper_graph = SmartScraperGraph(
    prompt="List me all the projects with their description.",
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
