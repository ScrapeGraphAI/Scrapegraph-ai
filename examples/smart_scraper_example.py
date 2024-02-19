""" 
Basic example of scraping pipeline using SmartScraper
"""
import os
from dotenv import load_dotenv
from scrapegraphai.graphs import SmartScraper

load_dotenv()

openai_key = os.getenv("OPENAI_APIKEY")
if not openai_key:
    print("Error: OpenAI API key not found in environment variables.")
llm_config = {
    "api_key": openai_key,
    "model_name": "gpt-3.5-turbo",
}

smart_scraper = SmartScraper("List me all the titles and project descriptions",
                             "https://perinim.github.io/projects/", llm_config)

answer = smart_scraper.run()
print(answer)
