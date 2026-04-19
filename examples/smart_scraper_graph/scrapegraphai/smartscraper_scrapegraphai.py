"""
Extract structured data from a webpage using scrapegraph-py v2 API.
Replaces the old smartscraper() call with extract().
"""

import json
import os

from dotenv import load_dotenv
from scrapegraph_py import Client

load_dotenv()

api_key = os.getenv("SCRAPEGRAPH_API_KEY")
if not api_key:
    raise ValueError("SCRAPEGRAPH_API_KEY not found in environment variables")

with Client(api_key=api_key) as client:
    response = client.extract(
        url="https://scrapegraphai.com",
        prompt="Extract the founders' informations",
    )
    print(json.dumps(response, indent=2))
