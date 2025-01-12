import asyncio
import json
import os

from aiohttp import ClientError
from dotenv import load_dotenv

from scrapegraphai.docloaders.chromium import (  # Import your ChromiumLoader class
    ChromiumLoader,
)
from scrapegraphai.graphs import SmartScraperGraph
from scrapegraphai.utils import prettify_exec_info

# Load environment variables for API keys
load_dotenv()


# ************************************************
# Define function to analyze content with ScrapegraphAI
# ************************************************
async def analyze_content_with_scrapegraph(content: str):
    """
    Analyze scraped content using ScrapegraphAI.

    Args:
        content (str): The scraped HTML or text content.

    Returns:
        dict: The result from ScrapegraphAI analysis.
    """
    try:
        # Initialize ScrapegraphAI SmartScraperGraph
        smart_scraper = SmartScraperGraph(
            prompt="Summarize the main content of this webpage and extract any contact information.",
            source=content,  # Pass the content directly
            config={
                "llm": {
                    "api_key": os.getenv("OPENAI_API_KEY"),
                    "model": "openai/gpt-4o",
                },
                "verbose": True,
            },
        )
        result = smart_scraper.run()
        return result
    except Exception as e:
        print(f"❌ ScrapegraphAI analysis failed: {e}")
        return {"error": str(e)}


# ************************************************
# Test scraper and ScrapegraphAI pipeline
# ************************************************
async def test_scraper_with_analysis(scraper: ChromiumLoader, urls: list):
    """
    Test scraper for the given backend and URLs, then analyze content with ScrapegraphAI.

    Args:
        scraper (ChromiumLoader): The ChromiumLoader instance.
        urls (list): A list of URLs to scrape.
    """
    for url in urls:
        try:
            print(f"\n🔎 Scraping: {url} using {scraper.backend}...")
            result = await scraper.scrape(url)

            if "Error" in result or not result.strip():
                print(f"❌ Failed to scrape {url}: {result}")
            else:
                print(
                    f"✅ Successfully scraped {url}. Content (first 200 chars): {result[:200]}"
                )

                # Pass scraped content to ScrapegraphAI for analysis
                print("🤖 Analyzing content with ScrapegraphAI...")
                analysis_result = await analyze_content_with_scrapegraph(result)
                print("📝 Analysis Result:")
                print(json.dumps(analysis_result, indent=4))

        except ClientError as ce:
            print(f"❌ Network error while scraping {url}: {ce}")
        except Exception as e:
            print(f"❌ Unexpected error while scraping {url}: {e}")


# ************************************************
# Main Execution
# ************************************************
async def main():
    urls_to_scrape = [
        "https://example.com",
        "https://www.python.org",
        "https://invalid-url.test",
    ]

    # Test with Playwright backend
    print("\n--- Testing Playwright Backend ---")
    try:
        scraper_playwright_chromium = ChromiumLoader(
            urls=urls_to_scrape,
            backend="playwright",
            headless=True,
            browser_name="chromium",
        )
        await test_scraper_with_analysis(scraper_playwright_chromium, urls_to_scrape)

        scraper_playwright_firefox = ChromiumLoader(
            urls=urls_to_scrape,
            backend="playwright",
            headless=True,
            browser_name="firefox",
        )
        await test_scraper_with_analysis(scraper_playwright_firefox, urls_to_scrape)
    except ImportError as ie:
        print(f"❌ Playwright ImportError: {ie}")
    except Exception as e:
        print(f"❌ Error initializing Playwright ChromiumLoader: {e}")

    # Test with Selenium backend
    print("\n--- Testing Selenium Backend ---")
    try:
        scraper_selenium_chromium = ChromiumLoader(
            urls=urls_to_scrape,
            backend="selenium",
            headless=True,
            browser_name="chromium",
        )
        await test_scraper_with_analysis(scraper_selenium_chromium, urls_to_scrape)

        scraper_selenium_firefox = ChromiumLoader(
            urls=urls_to_scrape,
            backend="selenium",
            headless=True,
            browser_name="firefox",
        )
        await test_scraper_with_analysis(scraper_selenium_firefox, urls_to_scrape)
    except ImportError as ie:
        print(f"❌ Selenium ImportError: {ie}")
    except Exception as e:
        print(f"❌ Error initializing Selenium ChromiumLoader: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("❌ Program interrupted by user.")
    except Exception as e:
        print(f"❌ Program crashed: {e}")
