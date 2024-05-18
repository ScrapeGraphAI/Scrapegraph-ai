""" 
Basic example of scraping pipeline using SmartScraper
"""

import os
from dotenv import load_dotenv
from scrapegraphai.graphs import MultipleSearchGraph
from scrapegraphai.utils import prettify_exec_info

load_dotenv()


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
        "model": "gpt-3.5-turbo",
    },
    "verbose": True,
    "headless": False,
    "schema": schema,
}



multiple_search_graph = MultipleSearchGraph(
    prompt="List me all the projects with their description",
    source= [
        "https://www.linkedin.com/jobs/machine-learning-engineer-offerte-di-lavoro/?currentJobId=3889037104&originalSubdomain=it",
        "https://www.glassdoor.com/Job/italy-machine-learning-engineer-jobs-SRCH_IL.0,5_IN120_KO6,31.html",
        "https://it.indeed.com/jobs?q=ML+engineer&vjk=3c2e6d27601ffaaa"
        ],
    config=graph_config,
)

result = multiple_search_graph.run()
print(result)

# ************************************************
# Get graph execution info
# ************************************************

graph_exec_info = multiple_search_graph.get_execution_info()
print(prettify_exec_info(graph_exec_info))
