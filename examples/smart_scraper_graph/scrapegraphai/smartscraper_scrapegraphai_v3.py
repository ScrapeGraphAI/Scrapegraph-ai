"""
Extract structured data using the scrapegraph-py v3 API (PR #84).
Uses ScrapeGraphAI client + ExtractRequest model + ApiResult wrapper.
"""

import json
import os

from dotenv import load_dotenv
from scrapegraph_py import ExtractRequest, ScrapeGraphAI

load_dotenv()

api_key = os.getenv("SGAI_API_KEY") or os.getenv("SCRAPEGRAPH_API_KEY")
if not api_key:
    raise ValueError("SGAI_API_KEY not found in environment variables")

with ScrapeGraphAI(api_key=api_key) as sgai:
    result = sgai.extract(
        ExtractRequest(
            url="https://scrapegraphai.com",
            prompt="Extract the founders' informations",
        )
    )

    if result.status == "success":
        print(json.dumps(result.data.model_dump(by_alias=True), indent=2, default=str))
    else:
        raise RuntimeError(result.error)
