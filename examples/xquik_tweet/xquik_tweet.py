"""Extract structured fields from a public X post through Xquik."""

import os

from dotenv import load_dotenv

from scrapegraphai.graphs import SmartScraperGraph

load_dotenv()

graph = SmartScraperGraph(
    prompt="Extract the post text, author username, creation time, and metrics.",
    source="https://x.com/example/status/1893456789012345678",
    config={
        "llm": {
            "api_key": os.environ["OPENAI_API_KEY"],
            "model": "openai/gpt-4o-mini",
        },
        "xquik": {
            "api_key": os.environ["X_TWITTER_SCRAPER_API_KEY"],
            "timeout": 30,
        },
    },
)

print(graph.run())
