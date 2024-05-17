"""
Example of knowledge graph node
"""

import os
from scrapegraphai.models import OpenAI
from scrapegraphai.nodes import KnowledgeGraphNode

job_postings = {
    "Job Postings": {
        "Company A": [
            {
                "title": "Software Engineer",
                "description": "Develop and maintain software applications.",
                "location": "New York, NY",
                "date_posted": "2024-05-01",
                "requirements": ["Python", "Django", "REST APIs"]
            },
            {
                "title": "Data Scientist",
                "description": "Analyze and interpret complex data.",
                "location": "San Francisco, CA",
                "date_posted": "2024-05-05",
                "requirements": ["Python", "Machine Learning", "SQL"]
            }
        ],
        "Company B": [
            {
                "title": "Project Manager",
                "description": "Manage software development projects.",
                "location": "Boston, MA",
                "date_posted": "2024-04-20",
                "requirements": ["Project Management", "Agile", "Scrum"]
            }
        ]
    }
}



# ************************************************
# Define the configuration for the graph
# ************************************************

openai_key = os.getenv("OPENAI_APIKEY")

graph_config = {
    "llm": {
        "api_key": openai_key,
        "model": "gpt-4o",
        "temperature": 0,
    },
}

# ************************************************
# Define the node
# ************************************************

llm_model = OpenAI(graph_config["llm"])

robots_node = KnowledgeGraphNode(
    input="answer & user_prompt",
    output=["is_scrapable"],
    node_config={"llm_model": llm_model,
                 "headless": False
                 }
)

# ************************************************
# Test the node
# ************************************************

state = {
    "url": "https://twitter.com/home"
}

result = robots_node.execute(state)

print(result)
