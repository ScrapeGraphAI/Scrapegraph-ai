""" 
Basic example of scraping pipeline using ScriptCreatorGraph
"""

import os
from dotenv import load_dotenv
from scrapegraphai.graphs import ScriptCreatorMultiGraph
from scrapegraphai.utils import prettify_exec_info
from langchain_openai import AzureChatOpenAI
from langchain_openai import AzureOpenAIEmbeddings

load_dotenv()

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
graph_config = {
    "llm": {"model_instance": llm_model_instance},
    "embeddings": {"model_instance": embedder_model_instance},
    "library": "beautifulsoup"
}


# ************************************************
# Create the ScriptCreatorGraph instance and run it
# ************************************************

urls=[
    "https://schultzbergagency.com/emil-raste-karlsen/",
    "https://schultzbergagency.com/johanna-hedberg/",
]

# ************************************************
# Create the ScriptCreatorGraph instance and run it
# ************************************************

script_creator_graph = ScriptCreatorMultiGraph(
    prompt="Find information about actors",
    # also accepts a string with the already downloaded HTML code
    source=urls,
    config=graph_config
)

result = script_creator_graph.run()
print(result)

# ************************************************
# Get graph execution info
# ************************************************

graph_exec_info = script_creator_graph.get_execution_info()
print(prettify_exec_info(graph_exec_info))
