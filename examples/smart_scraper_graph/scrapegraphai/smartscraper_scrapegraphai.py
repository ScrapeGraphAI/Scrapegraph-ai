"""
Example implementation using scrapegraph-py v2 client directly.
"""

import json
import os
from dotenv import load_dotenv
from scrapegraph_py import Client
from scrapegraph_py.logger import sgai_logger

def main():
    # Load environment variables from .env file
    load_dotenv()

    # Get API key from environment variables
    api_key = os.getenv("SCRAPEGRAPH_API_KEY")
    if not api_key:
        raise ValueError("SCRAPEGRAPH_API_KEY not found in environment variables")

    # Set up logging
    sgai_logger.set_logging(level="INFO")

    # Initialize the client with API key from environment
    sgai_client = Client(api_key=api_key)

    try:
        # Extract request (v2 API - replaces smartscraper)
        response = sgai_client.extract(
            url="https://scrapegraphai.com",
            prompt="Extract the founders' informations"
        )

        # Print the response
        print(json.dumps(response, indent=2))

    except Exception as e:
        print(f"Error occurred: {str(e)}")
    finally:
        # Always close the client
        sgai_client.close()

if __name__ == "__main__":
    main()
