from yosoai.graphs import SmartScraper

OPENAI_API_KEY = ''

llm_config = {
    "api_key": OPENAI_API_KEY,
    "model_name": "gpt-3.5-turbo",
}

url = "https://perinim.github.io/projects/"
prompt = "List me all the titles and project descriptions"

smart_scraper = SmartScraper(prompt, url, llm_config)

answer = smart_scraper.run()
print(answer)

