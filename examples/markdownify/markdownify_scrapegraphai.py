"""
Example script demonstrating the markdownify functionality
"""

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

    # Example 1: Convert a website to Markdown
    print("Example 1: Converting website to Markdown")
    print("-" * 50)
    response = sgai_client.markdownify(
        website_url="https://example.com"
    )
    print("Markdown output:")
    print(response["result"])  # Access the result key from the dictionary
    print("\nMetadata:")
    print(response.get("metadata", {}))  # Use get() with default value
    print("\n" + "=" * 50 + "\n")
if __name__ == "__main__":
    main()
