""" 
Basic example of scraping pipeline using SmartScraper
"""

import os
import json
from dotenv import load_dotenv
from scrapegraphai.graphs import SmartScraperMultiConcatGraph
from langchain_community.llms import HuggingFaceEndpoint
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings

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
