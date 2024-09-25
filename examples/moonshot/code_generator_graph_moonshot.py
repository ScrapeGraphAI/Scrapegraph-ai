""" 
Basic example of scraping pipeline using Code Generator with schema
"""

import os, json
from typing import List
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_community.chat_models.moonshot import MoonshotChat
from scrapegraphai.graphs import CodeGeneratorGraph

load_dotenv()

# ************************************************
# Define the output schema for the graph
# ************************************************

class Project(BaseModel):
    title: str = Field(description="The title of the project")
    description: str = Field(description="The description of the project")

class Projects(BaseModel):
    projects: List[Project]

# ************************************************
# Define the configuration for the graph
# ************************************************

llm_instance_config = {
    "model": "moonshot-v1-8k",
    "base_url": "https://api.moonshot.cn/v1",
    "moonshot_api_key": os.getenv("MOONLIGHT_API_KEY"),
}

llm_model_instance = MoonshotChat(**llm_instance_config)

graph_config = {
    "llm": {
        "model_instance": llm_model_instance, 
        "model_tokens": 10000
    },
    "verbose": True,
    "headless": False,
    "reduction": 2,
    "max_iterations": {
        "overall": 10,
        "syntax": 3,
        "execution": 3,
        "validation": 3,
        "semantic": 3
    },
    "output_file_name": "extracted_data.py"
}

# ************************************************
# Create the SmartScraperGraph instance and run it
# ************************************************

code_generator_graph = CodeGeneratorGraph(
    prompt="List me all the projects with their description",
    source="https://perinim.github.io/projects/",
    schema=Projects,
    config=graph_config
)

result = code_generator_graph.run()
print(result)