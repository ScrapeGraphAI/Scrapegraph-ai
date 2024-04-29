"""
Example of custom graph using existing nodes
"""

import os
from dotenv import load_dotenv
from scrapegraphai.models import OpenAI
from scrapegraphai.graphs import BaseGraph
from scrapegraphai.nodes import FetchNode, GenerateAnswerNode
load_dotenv()

# ************************************************
# Define the configuration for the graph
# ************************************************

openai_key = os.getenv("OPENAI_APIKEY")

graph_config = {
    "llm": {
        "api_key": openai_key,
        "model": "gpt-3.5-turbo",
        "temperature": 0,
        "streaming": True
    },
}

# ************************************************
# Define the graph nodes
# ************************************************

llm_model = OpenAI(graph_config["llm"])

# define the nodes for the graph
fetch_node = FetchNode(
    input="url | local_dir",
    output=["doc"],
)
generate_answer_node = GenerateAnswerNode(
    input="user_prompt & (relevant_chunks | parsed_doc | doc)",
    output=["answer"],
    node_config={"llm": llm_model},
)

# ************************************************
# Create the graph by defining the connections
# ************************************************

graph = BaseGraph(
    nodes={
        fetch_node,
        generate_answer_node,
    },
    edges={
        (fetch_node, generate_answer_node)
    },
    entry_point=fetch_node
)

# ************************************************
# Execute the graph
# ************************************************

subtree_text = '''
div>div -> "This is a paragraph" \n
div>ul>li>a>span -> "This is a list item 1" \n
div>ul>li>a>span -> "This is a list item 2" \n
div>ul>li>a>span -> "This is a list item 3"
'''

subtree_simplified_html = '''
<div>
    <div>This is a paragraph</div>
    <ul>
        <li>
            <span>This is a list item 1</span>
        </li>
        <li>
            <span>This is a list item 2</span>
        </li>
        <li>
            <span>This is a list item 3</span>
        </li>
    </ul>
</div>
'''

subtree_dict_simple = {
    "div": {
        "text": {
            "content": "This is a paragraph",
            "path_to_fork": "div>div",
        },
        "ul": {
            "path_to_fork": "div>ul",
            "texts": [
                {
                    "content": "This is a list item 1",
                    "path_to_fork": "ul>li>a>span",
                },
                {
                    "content": "This is a list item 2",
                    "path_to_fork": "ul>li>a>span",
                },
                {
                    "content": "This is a list item 3",
                    "path_to_fork": "ul>li>a>span",
                }
            ]
        }
    }
}


subtree_dict_complex = {
    "div": {
        "text": {
            "content": "This is a paragraph",
            "path_to_fork": "div>div",
            "attributes": {
                "classes": ["paragraph"],
                "ids": ["paragraph"],
                "hrefs": ["https://www.example.com"]
            }
        },
        "ul": {
            "text1":{
                "content": "This is a list item 1",
                "path_to_fork": "ul>li>a>span",
                "attributes": {
                    "classes": ["list-item", "item-1"],
                    "ids": ["item-1"],
                    "hrefs": ["https://www.example.com"]
                }
            },
            "text2":{
                "content": "This is a list item 2",
                "path_to_fork": "ul>li>a>span",
                "attributes": {
                    "classes": ["list-item", "item-2"],
                    "ids": ["item-2"],
                    "hrefs": ["https://www.example.com"]
                }
            }
        }
    }
}

result, execution_info = graph.execute({
    "user_prompt": "How many list items are there in the document?",
    "local_dir": str(subtree_dict_simple)
})

# get the answer from the result
result = result.get("answer", "No answer found.")
print(result)
