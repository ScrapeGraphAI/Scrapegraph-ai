"""
Basic example of scraping pipeline using SmartScraper
"""
from scrapegraphai.graphs import SmartScraperGraph
OPENAI_API_KEY = "YOUR_API_KEY"


llm_config = {
    "api_key": OPENAI_API_KEY,
    "model_name": "gpt-3.5-turbo",
}

smart_scraper_graph = SmartScraperGraph("List me all the titles and project descriptions",
                                        "https://perinim.github.io/projects/", llm_config)

answer = smart_scraper_graph.run()
print(answer["projects"][0])
