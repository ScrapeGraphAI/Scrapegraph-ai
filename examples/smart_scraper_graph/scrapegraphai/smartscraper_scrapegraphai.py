"""
Extract structured data from a webpage using scrapegraph-py.
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
    result = sgai.extract(
        "Extract the founders' informations",
        url="https://scrapegraphai.com",
    )

    if result.status != "success":
        raise RuntimeError(result.error)

    print(json.dumps(result.data.model_dump(by_alias=True), indent=2, default=str))
