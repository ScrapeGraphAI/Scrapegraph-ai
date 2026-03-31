"""
Example implementation of search-based scraping using Scrapegraph AI v2 API.
This example demonstrates how to use the search endpoint to extract information from the web.
"""

import json
import os
from dotenv import load_dotenv
from scrapegraph_py import Client
from scrapegraph_py.logger import sgai_logger

def main():
    # Load environment variables
    load_dotenv()

    # Get API key
    api_key = os.getenv("SCRAPEGRAPH_API_KEY")
    if not api_key:
        raise ValueError("SCRAPEGRAPH_API_KEY not found in environment variables")

    # Configure logging
    sgai_logger.set_logging(level="INFO")

    # Initialize client
    sgai_client = Client(api_key=api_key)

    try:
        # Search request (v2 API - replaces searchscraper)
        print("\nSearching for information...")

        search_response = sgai_client.search(
            query="Extract webpage information"
        )
        print(json.dumps(search_response, indent=2))

    except Exception as e:
        print(f"\nError occurred: {str(e)}")
    finally:
        # Always close the client
        sgai_client.close()

if __name__ == "__main__":
    main()
