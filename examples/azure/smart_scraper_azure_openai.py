""" 
Basic example of scraping pipeline using SmartScraper using Azure OpenAI Key
"""

import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_openai import AzureOpenAIEmbeddings
from scrapegraphai.graphs import SmartScraperGraph
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
# Create the SmartScraperGraph instance and run it
# ************************************************

graph_config = {
    "llm": {"model_instance": llm_model_instance},
    "embeddings": {"model_instance": embedder_model_instance}
}

smart_scraper_graph = SmartScraperGraph(
    prompt="""List me all the events, with the following fields: company_name, event_name, event_start_date, event_start_time, 
    event_end_date, event_end_time, location, event_mode, event_category, 
    third_party_redirect, no_of_days, 
    time_in_hours, hosted_or_attending, refreshments_type, 
    registration_available, registration_link""",
    # also accepts a string with the already downloaded HTML code
    source="https://www.hmhco.com/event",
    config=graph_config
)

result = smart_scraper_graph.run()
print(result)

# ************************************************
# Get graph execution info
# ************************************************

graph_exec_info = smart_scraper_graph.get_execution_info()
print(prettify_exec_info(graph_exec_info))
