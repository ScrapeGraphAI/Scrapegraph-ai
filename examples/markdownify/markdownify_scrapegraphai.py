"""
Example script demonstrating the scrape functionality (v2 API - replaces markdownify)
"""

import json
import os
from dotenv import load_dotenv
from scrapegraph_py import Client
from scrapegraph_py.logger import sgai_logger

def main():
    # Load environment variables
    load_dotenv()

    # Set up logging
    sgai_logger.set_logging(level="INFO")

    # Initialize the client
    api_key = os.getenv("SCRAPEGRAPH_API_KEY")
    if not api_key:
        raise ValueError("SCRAPEGRAPH_API_KEY environment variable not found")
    sgai_client = Client(api_key=api_key)

    # Scrape a website as markdown (v2 API - replaces markdownify)
    print("Scraping website as Markdown")
    print("-" * 50)
    response = sgai_client.scrape(
        url="https://example.com"
    )
    print(json.dumps(response, indent=2))

if __name__ == "__main__":
    main()
