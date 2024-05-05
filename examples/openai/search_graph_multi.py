"""
Example of custom graph using existing nodes
"""

import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from scrapegraphai.models import OpenAI
from scrapegraphai.graphs import BaseGraph, SmartScraperGraph
from scrapegraphai.nodes import SearchInternetNode, GraphIteratorNode, MergeAnswersNode
load_dotenv()

# ************************************************
# Define the configuration for the graph
# ************************************************

openai_key = os.getenv("OPENAI_APIKEY")

graph_config = {
    "llm": {
        "api_key": openai_key,
        "model": "gpt-3.5-turbo",
    },
}

# ************************************************
# Create a SmartScraperGraph instance
# ************************************************

smart_scraper_graph = SmartScraperGraph(
    prompt="",
    source="",
    config=graph_config
)

# ************************************************
# Define the graph nodes
# ************************************************

llm_model = OpenAI(graph_config["llm"])
embedder = OpenAIEmbeddings(api_key=llm_model.openai_api_key)

search_internet_node = SearchInternetNode(
    input="user_prompt",
    output=["urls"],
    node_config={
        "llm_model": llm_model,
        "verbose": True,
    }
)

graph_iterator_node = GraphIteratorNode(
    input="user_prompt & urls",
    output=["results"],
    node_config={
        "graph_instance": smart_scraper_graph,
        "verbose": True,
    }
)

merge_answers_node = MergeAnswersNode(
    input="user_prompt & results",
    output=["answer"],
    node_config={
        "llm_model": llm_model,
        "verbose": True,
    }
)

# ************************************************
# Create the graph by defining the connections
# ************************************************

graph = BaseGraph(
    nodes=[
        search_internet_node,
        graph_iterator_node,
        merge_answers_node
    ],
    edges=[
        (search_internet_node, graph_iterator_node),
        (graph_iterator_node, merge_answers_node)
    ],
    entry_point=search_internet_node
)

# ************************************************
# Execute the graph
# ************************************************

result, execution_info = graph.execute({
    "user_prompt": "List me all the typical Chioggia dishes."
})

# get the answer from the result
result = result.get("answer", "No answer found.")
print(result)
