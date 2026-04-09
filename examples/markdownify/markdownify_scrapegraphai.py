"""
Scrape a webpage as clean markdown using scrapegraph-py v2 API.
Replaces the old markdownify() call with scrape().
"""

import json
import os

from dotenv import load_dotenv
from scrapegraph_py import Client

load_dotenv()

api_key = os.getenv("SCRAPEGRAPH_API_KEY")
if not api_key:
    raise ValueError("SCRAPEGRAPH_API_KEY environment variable not found")

with Client(api_key=api_key) as client:
    response = client.scrape(url="https://example.com")
    print(json.dumps(response, indent=2))
