import asyncio
from chromium import ChromiumLoader  # Import the ChromiumLoader class from chromium.py
from aiohttp import ClientError


async def test_scraper(scraper: ChromiumLoader, urls: list):
    """
    Test scraper for the given backend and URLs.
    Args:
        scraper (ChromiumLoader): The ChromiumLoader instance.
        urls (list): A list of URLs to scrape.
    """
    for url in urls:
        try:
            print(f"Scraping: {url} using {scraper.backend}...")
            result = await scraper.scrape(url)
            if "Error" in result or not result.strip():
                print(f"❌ Failed to scrape {url}: {result}")
            else:
                print(f"✅ Successfully scraped {url}. Content (first 200 chars): {result[:200]}")
        except ClientError as ce:
            print(f"❌ Network error while scraping {url}: {ce}")
        except Exception as e:
            print(f"❌ Unexpected error while scraping {url}: {e}")


async def main():
    urls_to_scrape = ["https://example.com", "https://www.python.org", "https://invalid-url.test"]

    # Test with Playwright backend
    print("\n--- Testing Playwright Backend ---")
    try:
        scraper_playwright = ChromiumLoader(urls=urls_to_scrape, backend="playwright", headless=True)
        await test_scraper(scraper_playwright, urls_to_scrape)
    except ImportError as ie:
        print(f"❌ Playwright ImportError: {ie}")
    except Exception as e:
        print(f"❌ Error initializing Playwright ChromiumLoader: {e}")

    # Test with Selenium backend
    print("\n--- Testing Selenium Backend ---")
    try:
        scraper_selenium = ChromiumLoader(urls=urls_to_scrape, backend="selenium", headless=True)
        await test_scraper(scraper_selenium, urls_to_scrape)
    except ImportError as ie:
        print(f"❌ Selenium ImportError: {ie}")
    except Exception as e:
        print(f"❌ Error initializing Selenium ChromiumLoader: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program interrupted by user.")
    except Exception as e:
        print(f"❌ Program crashed: {e}")
