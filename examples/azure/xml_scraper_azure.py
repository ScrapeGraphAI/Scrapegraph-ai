""" 
Basic example of scraping pipeline using SmartScraper using Azure OpenAI Key
"""

import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_openai import AzureOpenAIEmbeddings
from scrapegraphai.graphs import XMLScraperGraph
from scrapegraphai.utils import prettify_exec_info


# required environment variable in .env
# AZURE_OPENAI_ENDPOINT
# AZURE_OPENAI_CHAT_DEPLOYMENT_NAME
# MODEL_NAME
# AZURE_OPENAI_API_KEY
# OPENAI_API_TYPE
# AZURE_OPENAI_API_VERSION
# AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT_NAME
load_dotenv()

FILE_NAME = "inputs/books.xml"
curr_dir = os.path.dirname(os.path.realpath(__file__))
file_path = os.path.join(curr_dir, FILE_NAME)

with open(file_path, 'r', encoding="utf-8") as file:
    text = file.read()


# ************************************************
# Initialize the model instances
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
# Create the XMLScraperGraph instance and run it
# ************************************************

graph_config = {
    "llm": {"model_instance": llm_model_instance},
    "embeddings": {"model_instance": embedder_model_instance}
}

smart_scraper_graph = XMLScraperGraph(
    prompt="List me all the authors, title and genres of the books",
    source=text,  # Pass the content of the file, not the file object
    config=graph_config
)

result = smart_scraper_graph.run()
print(result)

# ************************************************
# Get graph execution info
# ************************************************

graph_exec_info = smart_scraper_graph.get_execution_info()
print(prettify_exec_info(graph_exec_info))
