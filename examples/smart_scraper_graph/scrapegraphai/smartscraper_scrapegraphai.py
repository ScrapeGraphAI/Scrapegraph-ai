"""
Example implementation using scrapegraph-py client directly.
"""

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
        raise ValueError("SCRAPEGRAPH_API_KEY non trovato nelle variabili d'ambiente")

    # Set up logging
    sgai_logger.set_logging(level="INFO")

    # Initialize the client with API key from environment
    sgai_client = Client(api_key=api_key)

    try:
        # SmartScraper request
        response = sgai_client.smartscraper(
            website_url="https://scrapegraphai.com",
            user_prompt="Extract the founders' informations"
        )

        # Print the response
        print(f"Request ID: {response['request_id']}")
        print(f"Result: {response['result']}")
        if response.get('reference_urls'):
            print(f"Reference URLs: {response['reference_urls']}")

    except Exception as e:
        print(f"Error occurred: {str(e)}")
    finally:
        # Always close the client
        sgai_client.close()

if __name__ == "__main__":
    main()
