"""
Basic example of scraping pipeline using CSVScraperMultiGraph from CSV documents
"""

import os
import pandas as pd
from scrapegraphai.graphs import CSVScraperMultiGraph
from scrapegraphai.utils import convert_to_csv, convert_to_json, prettify_exec_info
from langchain_community.llms import HuggingFaceEndpoint
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings

# ************************************************
# Read the CSV file
# ************************************************

FILE_NAME = "inputs/username.csv"
curr_dir = os.path.dirname(os.path.realpath(__file__))
file_path = os.path.join(curr_dir, FILE_NAME)

text = pd.read_csv(file_path)

# ************************************************
# Define the configuration for the graph
# ************************************************
HUGGINGFACEHUB_API_TOKEN = os.getenv('HUGGINGFACEHUB_API_TOKEN')

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


# ************************************************
# Create the CSVScraperMultiGraph instance and run it
# ************************************************

csv_scraper_graph = CSVScraperMultiGraph(
    prompt="List me all the last names",
    source=[str(text), str(text)],
    config=graph_config
)

result = csv_scraper_graph.run()
print(result)

# ************************************************
# Get graph execution info
# ************************************************

graph_exec_info = csv_scraper_graph.get_execution_info()
print(prettify_exec_info(graph_exec_info))

# Save to json or csv
convert_to_csv(result, "result")
convert_to_json(result, "result")
