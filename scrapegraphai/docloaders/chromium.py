"""
chromiumloader module
"""
import asyncio
from typing import Any, AsyncIterator, Iterator, List, Optional
from langchain_community.document_loaders.base import BaseLoader
from langchain_core.documents import Document
import aiohttp
import async_timeout
from ..utils import Proxy, dynamic_import, get_logger, parse_or_search_proxy

logger = get_logger("web-loader")

class ChromiumLoader(BaseLoader):
    """scrapes HTML pages from URLs using a (headless) instance of the
    Chromium web driver with proxy protection

    Attributes:
        backend: The web driver backend library; defaults to 'playwright'.
        browser_config: A dictionary containing additional browser kwargs.
        headless: whether to run browser in headless mode.
        proxy: A dictionary containing proxy settings; None disables protection.
        urls: A list of URLs to scrape content from.
    """

    RETRY_LIMIT = 3
    TIMEOUT = 10

    def __init__(
        self,
        urls: List[str],
        *,
        backend: str = "playwright",
        headless: bool = True,
        proxy: Optional[Proxy] = None,
        load_state: str = "domcontentloaded",
        **kwargs: Any,
    ):
        """Initialize the loader with a list of URL paths.

        Args:
            backend: The web driver backend library; defaults to 'playwright'.
            headless: whether to run browser in headless mode.
            proxy: A dictionary containing proxy information; None disables protection.
            urls: A list of URLs to scrape content from.
            kwargs: A dictionary containing additional browser kwargs.

        Raises:
            ImportError: If the required backend package is not installed.
        """
        message = (
            f"{backend} is required for ChromiumLoader. "
            f"Please install it with `pip install {backend}`."
        )

        dynamic_import(backend, message)

        self.backend = backend
        self.browser_config = kwargs
        self.headless = headless
        self.proxy = parse_or_search_proxy(proxy) if proxy else None
        self.urls = urls
        self.load_state = load_state

    async def ascrape_undetected_chromedriver(self, url: str) -> str:
        """
        Asynchronously scrape the content of a given URL using undetected chrome with Selenium.

        Args:
            url (str): The URL to scrape.

        Returns:
            str: The scraped HTML content or an error message if an exception occurs.
        """
        import undetected_chromedriver as uc

        logger.info(f"Starting scraping with {self.backend}...")
        results = ""
        attempt = 0

        while attempt < self.RETRY_LIMIT:
            try:
                async with async_timeout.timeout(self.TIMEOUT):
                    driver = uc.Chrome(headless=self.headless)
                    driver.get(url)
                    results = driver.page_source
                    logger.info(f"Successfully scraped {url}")
                    break
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                attempt += 1
                logger.error(f"Attempt {attempt} failed: {e}")
                if attempt == self.RETRY_LIMIT:
                    results = f"Error: Network error after {self.RETRY_LIMIT} attempts - {e}"
            finally:
                driver.quit()

        return results

    async def ascrape_playwright(self, url: str) -> str:
        """
        Asynchronously scrape the content of a given URL using Playwright's async API.

        Args:
            url (str): The URL to scrape.

        Returns:
            str: The scraped HTML content or an error message if an exception occurs.
        """
        from playwright.async_api import async_playwright
        from undetected_playwright import Malenia

        logger.info(f"Starting scraping with {self.backend}...")
        results = ""
        attempt = 0

        while attempt < self.RETRY_LIMIT:
            try:
                async with async_playwright() as p, async_timeout.timeout(self.TIMEOUT):
                    browser = await p.chromium.launch(
                        headless=self.headless, proxy=self.proxy, **self.browser_config
                    )
                    context = await browser.new_context()
                    await Malenia.apply_stealth(context)
                    page = await context.new_page()
                    await page.goto(url, wait_until="domcontentloaded")
                    await page.wait_for_load_state(self.load_state)
                    results = await page.content()
                    logger.info("Content scraped")
                    break
            except (aiohttp.ClientError, asyncio.TimeoutError, Exception) as e:
                attempt += 1
                logger.error(f"Attempt {attempt} failed: {e}")
                if attempt == self.RETRY_LIMIT:
                    results = f"Error: Network error after {self.RETRY_LIMIT} attempts - {e}"
            finally:
                await browser.close()

        return results

    async def ascrape_with_js_support(self, url: str) -> str:
        """
        Asynchronously scrape the content of a given URL by rendering JavaScript using Playwright.

        Args:
            url (str): The URL to scrape.

        Returns:
            str: The fully rendered HTML content after JavaScript execution, 
            or an error message if an exception occurs.
        """
        from playwright.async_api import async_playwright

        logger.info(f"Starting scraping with JavaScript support for {url}...")
        results = ""
        attempt = 0

        while attempt < self.RETRY_LIMIT:
            try:
                async with async_playwright() as p, async_timeout.timeout(self.TIMEOUT):
                    browser = await p.chromium.launch(
                        headless=self.headless, proxy=self.proxy, **self.browser_config
                    )
                    context = await browser.new_context()
                    page = await context.new_page()
                    await page.goto(url, wait_until="networkidle")
                    results = await page.content()
                    logger.info("Content scraped after JavaScript rendering")
                    break
            except (aiohttp.ClientError, asyncio.TimeoutError, Exception) as e:
                attempt += 1
                logger.error(f"Attempt {attempt} failed: {e}")
                if attempt == self.RETRY_LIMIT:
                    results = f"Error: Network error after {self.RETRY_LIMIT} attempts - {e}"
            finally:
                await browser.close()

        return results

    def lazy_load(self) -> Iterator[Document]:
        """
        Lazily load text content from the provided URLs.

        This method yields Documents one at a time as they're scraped,
        instead of waiting to scrape all URLs before returning.

        Yields:
            Document: The scraped content encapsulated within a Document object.
        """
        scraping_fn = getattr(self, f"ascrape_{self.backend}")

        for url in self.urls:
            html_content = asyncio.run(scraping_fn(url))
            metadata = {"source": url}
            yield Document(page_content=html_content, metadata=metadata)

    async def alazy_load(self) -> AsyncIterator[Document]:
        """
        Asynchronously load text content from the provided URLs.

        This method leverages asyncio to initiate the scraping of all provided URLs
        simultaneously. It improves performance by utilizing concurrent asynchronous
        requests. Each Document is yielded as soon as its content is available,
        encapsulating the scraped content.

        Yields:
            Document: A Document object containing the scraped content, along with its
            source URL as metadata.
        """
        scraping_fn = getattr(self, f"ascrape_{self.backend}")

        tasks = [scraping_fn(url) for url in self.urls]
        results = await asyncio.gather(*tasks)
        for url, content in zip(self.urls, results):
            metadata = {"source": url}
            yield Document(page_content=content, metadata=metadata)
