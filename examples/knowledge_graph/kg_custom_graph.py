"""
Example of custom graph for creating a knowledge graph
"""

import os, json
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings
from scrapegraphai.models import OpenAI
from scrapegraphai.graphs import BaseGraph, SmartScraperGraph
from scrapegraphai.nodes import GraphIteratorNode, MergeAnswersNode, KnowledgeGraphNode

load_dotenv()

# ************************************************
# Define the output schema
# ************************************************

schema= """{ 
    "Job Postings": { 
        "Company x": [ 
            { 
                "title": "...", 
                "description": "...", 
                "location": "...", 
                "date_posted": "..", 
                "requirements": ["...", "...", "..."] 
            }, 
            { 
                "title": "...", 
                "description": "...", 
                "location": "...", 
                "date_posted": "..", 
                "requirements": ["...", "...", "..."] 
            } 
        ], 
        "Company y": [ 
            { 
                "title": "...", 
                "description": "...", 
                "location": "...", 
                "date_posted": "..", 
                "requirements": ["...", "...", "..."] 
            } 
        ] 
    } 
}"""

# ************************************************
# Define the configuration for the graph
# ************************************************

openai_key = os.getenv("OPENAI_APIKEY")

graph_config = {
    "llm": {
        "api_key": openai_key,
        "model": "gpt-4o",
    },
    "verbose": True,
    "headless": False,
}

# ************************************************
# Define the graph nodes
# ************************************************

llm_model = OpenAI(graph_config["llm"])
embedder = OpenAIEmbeddings(api_key=llm_model.openai_api_key)

smart_scraper_instance = SmartScraperGraph(
    prompt="",
    source="",
    config=graph_config,
)

# ************************************************
# Define the graph nodes
# ************************************************

graph_iterator_node = GraphIteratorNode(
    input="user_prompt & urls",
    output=["results"],
    node_config={
        "graph_instance": smart_scraper_instance,
    }
)

merge_answers_node = MergeAnswersNode(
    input="user_prompt & results",
    output=["answer"],
    node_config={
        "llm_model": llm_model,
        "schema": schema
    }
)

knowledge_graph_node = KnowledgeGraphNode(
    input="user_prompt & answer",
    output=["kg"],
    node_config={
        "llm_model": llm_model,
    }
)

graph = BaseGraph(
    nodes=[
        graph_iterator_node,
        merge_answers_node,
        knowledge_graph_node
    ],
    edges=[
        (graph_iterator_node, merge_answers_node),
        (merge_answers_node, knowledge_graph_node)
    ],
    entry_point=graph_iterator_node
)

# ************************************************
# Execute the graph
# ************************************************

result, execution_info = graph.execute({
    "user_prompt": "List me all the Machine Learning Engineer job postings",
    "urls": [
        "https://www.linkedin.com/jobs/machine-learning-engineer-offerte-di-lavoro/?currentJobId=3889037104&originalSubdomain=it",
        "https://www.glassdoor.com/Job/italy-machine-learning-engineer-jobs-SRCH_IL.0,5_IN120_KO6,31.html",
        "https://it.indeed.com/jobs?q=ML+engineer&vjk=3c2e6d27601ffaaa"
        ],
})

# get the answer from the result
result = result.get("answer", "No answer found.")
print(json.dumps(result, indent=4))
