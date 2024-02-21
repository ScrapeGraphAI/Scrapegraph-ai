""" 
Basic example of scraping pipeline using SmartScraper
"""

import os
from dotenv import load_dotenv
from scrapegraphai.graphs import SmartScraperGraph

load_dotenv()

# Define the configuration for the language model
openai_key = os.getenv("OPENAI_APIKEY")
llm_config = {
    "api_key": openai_key,
    "model_name": "gpt-3.5-turbo",
}

# Define URL and prompt
url = "https://perinim.github.io/projects/"
prompt = "List me all the titles and project descriptions"

# Create the SmartScraperGraph instance
smart_scraper_graph = SmartScraperGraph(prompt, url, llm_config)

answer = smart_scraper_graph.run()
print(answer)
