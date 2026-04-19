"""
Search the web and extract AI-structured results using scrapegraph-py v2 API.
Replaces the old searchscraper() call with search().
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
    response = client.search(query="Extract webpage information")
    print(json.dumps(response, indent=2))
