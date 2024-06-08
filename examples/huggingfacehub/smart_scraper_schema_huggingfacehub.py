""" 
Basic example of scraping pipeline using SmartScraper using Azure OpenAI Key
"""

import os
from dotenv import load_dotenv
from scrapegraphai.graphs import SmartScraperGraph
from scrapegraphai.utils import prettify_exec_info
from langchain_community.llms import HuggingFaceEndpoint
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings

# ************************************************
# Define the output schema for the graph
# ************************************************

schema= """
    { 
    "Projects": [
        "Project #": 
            { 
                "title": "...", 
                "description": "...", 
            }, 
        "Project #": 
            { 
                "title": "...", 
                "description": "...", 
            } 
        ] 
    } 
"""

## required environment variable in .env
#HUGGINGFACEHUB_API_TOKEN
load_dotenv()

HUGGINGFACEHUB_API_TOKEN = os.getenv('HUGGINGFACEHUB_API_TOKEN')
# ************************************************
# Initialize the model instances
# ************************************************

repo_id = "mistralai/Mistral-7B-Instruct-v0.2"

llm_model_instance = HuggingFaceEndpoint(
    repo_id=repo_id, max_length=128, temperature=0.5, token=HUGGINGFACEHUB_API_TOKEN
)

embedder_model_instance = HuggingFaceInferenceAPIEmbeddings(
    api_key=HUGGINGFACEHUB_API_TOKEN, model_name="sentence-transformers/all-MiniLM-l6-v2"
)

# ************************************************
# Create the SmartScraperGraph instance and run it
# ************************************************

graph_config = {
    "llm": {"model_instance": llm_model_instance},
    "embeddings": {"model_instance": embedder_model_instance}
}

smart_scraper_graph = SmartScraperGraph(
    prompt="List me all the projects with their description",
    source="https://perinim.github.io/projects/",
    schema=schema,
    config=graph_config
)
result = smart_scraper_graph.run()
print(result)

# ************************************************
# Get graph execution info
# ************************************************

graph_exec_info = smart_scraper_graph.get_execution_info()
print(prettify_exec_info(graph_exec_info))
