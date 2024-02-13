from langchain_openai import ChatOpenAI
from yosoai.graph import SmartScraper

OPENAI_API_KEY = ''
llm = ChatOpenAI(api_key=OPENAI_API_KEY, model_name="gpt-3.5-turbo", temperature=0, streaming=True)

url = "https://perinim.github.io/projects/"
prompt = "List me all the titles and project descriptions"

smart_scraper = SmartScraper(prompt, url, llm)
answer = smart_scraper.run()

print(answer)

