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

# Define URL and PROMPT
URL = "https://www.google.com/search?client=safari&rls=en&q=ristoranti+trento&ie=UTF-8&oe=UTF-8"
PROMPT = "List me all the https inside the page"

# Create the SmartScraperGraph instance
smart_scraper_graph = SmartScraperGraph(PROMPT, URL, llm_config)

answer = smart_scraper_graph.run()
print(answer)
