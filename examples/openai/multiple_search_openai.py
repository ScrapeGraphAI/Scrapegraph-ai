""" 
Basic example of scraping pipeline using SmartScraper
"""

import os
from dotenv import load_dotenv
from scrapegraphai.graphs import MultipleSearchGraph
from scrapegraphai.utils import prettify_exec_info

load_dotenv()


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

schema= """{ 
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
}"""

multiple_search_graph = MultipleSearchGraph(
    prompt="List me all the projects with their description",
    source= ["https://perinim.github.io/projects/", "https://perinim.github.io/projects/"],
    config=graph_config,
    schema = schema
)

result = multiple_search_graph.run()
print(result)

# ************************************************
# Get graph execution info
# ************************************************

graph_exec_info = multiple_search_graph.get_execution_info()
print(prettify_exec_info(graph_exec_info))
