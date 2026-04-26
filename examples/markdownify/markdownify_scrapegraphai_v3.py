"""
Scrape a webpage as markdown using the scrapegraph-py SDK (>=2.1.1).
Uses the ScrapeGraphAI client with ergonomic kwargs and ApiResult wrapper.
"""

import json
import os

from dotenv import load_dotenv
from scrapegraph_py import ScrapeGraphAI

load_dotenv()

api_key = os.getenv("SGAI_API_KEY") or os.getenv("SCRAPEGRAPH_API_KEY")
if not api_key:
    raise ValueError("SGAI_API_KEY not found in environment variables")

with ScrapeGraphAI(api_key=api_key) as sgai:
    result = sgai.scrape("https://example.com")

    if result.status == "success":
        print(json.dumps(result.data.model_dump(by_alias=True), indent=2, default=str))
    else:
        raise RuntimeError(result.error)
