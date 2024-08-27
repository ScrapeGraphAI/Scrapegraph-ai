"""
Example of Search Link Graph
"""
import os
from dotenv import load_dotenv
from scrapegraphai.graphs import SearchLinkGraph
from scrapegraphai.utils import convert_to_csv, convert_to_json, prettify_exec_info
from langchain_openai import AzureChatOpenAI
from langchain_openai import AzureOpenAIEmbeddings

# ************************************************
# Define the configuration for the graph
# ************************************************

load_dotenv()

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

# ************************************************
# Create the SearchLinkGraph instance and run it
# ************************************************

search_link_graph = SearchLinkGraph(
    source="https://sport.sky.it/nba?gr=www",
    config=graph_config
)

result = search_link_graph.run()
print(result)

# ************************************************
# Get graph execution info
# ************************************************

graph_exec_info = search_link_graph.get_execution_info()
print(prettify_exec_info(graph_exec_info))

# Save to json and csv
convert_to_csv(result, "result")
convert_to_json(result, "result")
