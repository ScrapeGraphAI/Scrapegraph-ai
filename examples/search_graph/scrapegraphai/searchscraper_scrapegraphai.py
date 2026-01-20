"""
Example implementation of search-based scraping using Scrapegraph AI.
This example demonstrates how to use the searchscraper to extract information from the web.
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv
from scrapegraph_py import Client
from scrapegraph_py.logger import sgai_logger

def format_response(response: Dict[str, Any]) -> None:
    """
    Format and print the search response in a readable way.

    Args:
        response (Dict[str, Any]): The response from the search API
    """
    print("\n" + "="*50)
    print("SEARCH RESULTS")
    print("="*50)

    # Print request ID
    print(f"\nRequest ID: {response['request_id']}")

    # Print number of sources
    urls = response.get('reference_urls', [])
    print(f"\nSources Processed: {len(urls)}")

    # Print the extracted information
    print("\nExtracted Information:")
    print("-"*30)
    if isinstance(response['result'], dict):
        for key, value in response['result'].items():
            print(f"\n{key.upper()}:")
            if isinstance(value, list):
                for item in value:
                    print(f"  • {item}")
            else:
                print(f"  {value}")
    else:
        print(response['result'])

    # Print source URLs
    if urls:
        print("\nSources:")
        print("-"*30)
        for i, url in enumerate(urls, 1):
            print(f"{i}. {url}")
    print("\n" + "="*50)

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
        # Basic search scraper example
        print("\nSearching for information...")

        search_response = sgai_client.searchscraper(
            user_prompt="Extract webpage information"
        )
        format_response(search_response)

    except Exception as e:
        print(f"\nError occurred: {str(e)}")
    finally:
        # Always close the client
        sgai_client.close()

if __name__ == "__main__":
    main()
