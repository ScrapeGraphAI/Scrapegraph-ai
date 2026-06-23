"""
Experimental: Crawl4AI backend for ScrapeGraphAI.

Crawl4AI (https://github.com/unclecode/crawl4ai) is a Python async web crawler
with advanced markdown generation, content filtering, and structured data extraction.

This loader uses Crawl4AI's AsyncWebCrawler as an alternative document fetcher,
providing clean markdown output suitable for LLM consumption.

If Crawl4AI fails due to anti-bot protection (e.g. Cloudflare), the loader
automatically falls back to launching a stealth-hardened Chrome instance via
Playwright + Malenia and connecting Crawl4AI to it via CDP.

Usage in node_config:
    "experimental": {
        "backend": "crawl4ai",
        "crawl4ai": {
            "headless": true,
            "output_format": "markdown",
            "page_timeout": 30000,
            "viewport_width": 1920,
            "viewport_height": 1080,
            "cache_mode": null
        }
    }
"""

import asyncio
from typing import Any, AsyncIterator, Iterator, List, Optional

from langchain_core.documents import Document

from ..utils import get_logger

logger = get_logger("crawl4ai-loader")


class Crawl4aiLoader:
    """
    Document loader that fetches web pages using Crawl4AI's AsyncWebCrawler.

    Crawl4AI provides clean markdown output, content filtering, and JS rendering,
    making it an excellent alternative backend for ScrapeGraphAI.

    Attributes:
        headless: Whether to run browser in headless mode.
        page_timeout: Maximum page load time in milliseconds.
        output_format: Content format - "markdown", "html", or "text".
        urls: List of URLs to scrape.
        cache_mode: Crawl4AI cache mode (None = no cache).
        viewport: Browser viewport dimensions.
    """

    def __init__(
        self,
        urls: List[str],
        *,
        headless: bool = True,
        page_timeout: int = 60000,
        output_format: str = "markdown",
        viewport_width: int = 1920,
        viewport_height: int = 1080,
        cache_mode: Optional[str] = None,
        proxy: Optional[dict] = None,
        **kwargs: Any,
    ):
        self.urls = urls
        self.headless = headless
        self.page_timeout = page_timeout
        self.output_format = output_format
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self.cache_mode = cache_mode
        self.proxy = proxy
        self.browser_config = kwargs

    def _get_content(self, result, url: str) -> str:
        """Extract content from Crawl4AI result based on output_format."""
        if self.output_format == "markdown":
            content = getattr(result, "markdown", "") or ""
            if not content:
                content = getattr(result, "html", "") or ""
            return content
        elif self.output_format == "html":
            return getattr(result, "html", "") or ""
        elif self.output_format == "text":
            return getattr(result, "cleaned_html", "") or getattr(result, "html", "") or ""
        return getattr(result, "markdown", "") or getattr(result, "html", "") or ""

    async def _afetch_with_playwright_fallback(self, url: str) -> str:
        """Fallback: use Playwright + Malenia directly when Crawl4AI is blocked."""
        logger.info(f"Crawl4AI blocked, falling back to Playwright direct fetch: {url}")

        from playwright.async_api import async_playwright
        from undetected_playwright import Malenia
        import os

        raw_html = ""
        try:
            async with async_playwright() as p:
                args = [
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-web-security",
                    "--disable-features=IsolateOrigins,site-per-process",
                ]

                user_data_dir = os.path.join(os.path.expanduser("~"), ".scrapegraph", "chrome-profile")
                os.makedirs(user_data_dir, exist_ok=True)
                storage_path = os.path.join(os.path.expanduser("~"), ".scrapegraph", "chrome-data", "storage_state.json")

                storage_state = None
                if os.path.exists(storage_path):
                    try:
                        import json
                        with open(storage_path) as f:
                            storage_state = json.load(f)
                    except Exception:
                        pass

                context = await p.chromium.launch_persistent_context(
                    user_data_dir,
                    headless=self.headless,
                    channel="chrome",
                    args=args,
                    ignore_https_errors=True,
                )
                await Malenia.apply_stealth(context)

                if storage_state and "cookies" in storage_state:
                    try:
                        await context.add_cookies(storage_state["cookies"])
                    except Exception:
                        pass

                page = context.pages[0] if context.pages else await context.new_page()
                await page.goto(url, wait_until="domcontentloaded",
                                timeout=min(self.page_timeout, 90000))
                await page.wait_for_timeout(3000)
                raw_html = await page.content()

                # Save storage state
                try:
                    state = await context.storage_state()
                    with open(storage_path, "w") as f:
                        import json
                        json.dump(state, f)
                except Exception:
                    pass

                await context.close()
        except Exception as e:
            logger.warning(f"Playwright fallback error for {url}: {e}")
            return ""

        if not raw_html.strip():
            return ""

        if self.output_format == "html":
            return raw_html
        elif self.output_format == "text":
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(raw_html, "html.parser")
                return soup.get_text(separator="\n", strip=True)
            except ImportError:
                return raw_html
        else:
            try:
                import html2text
                converter = html2text.HTML2Text()
                converter.body_width = 0
                converter.ignore_links = False
                converter.ignore_images = False
                return converter.handle(raw_html)
            except ImportError:
                return raw_html

    async def afetch_page(self, url: str) -> str:
        """
        Fetch a single page using Crawl4AI.
        Falls back to CDP stealth mode if anti-bot protection is detected.
        """
        try:
            from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
        except ImportError:
            raise ImportError(
                "crawl4ai is required for Crawl4aiLoader. "
                "Install it with: pip install crawl4ai"
            )

        logger.info(f"Fetching via Crawl4AI: {url}")

        browser_kwargs = {
            "headless": self.headless,
            "viewport_width": self.viewport_width,
            "viewport_height": self.viewport_height,
            "enable_stealth": True,
            "ignore_https_errors": True,
            "extra_args": [
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",
            ],
            "headers": {
                "Accept-Language": "en-US,en;q=0.9,tr;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
            },
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        }
        if self.proxy:
            browser_kwargs["proxy_config"] = self.proxy

        browser_config = BrowserConfig(**browser_kwargs)

        crawler_config = CrawlerRunConfig(
            page_timeout=self.page_timeout,
            delay_before_return_html=4.0,
            verbose=False,
        )

        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url=url, config=crawler_config)

            if result.success:
                content = self._get_content(result, url)
                if not content:
                    logger.warning(f"Crawl4AI returned empty content for {url}")
                return content

            err = getattr(result, 'error_message', '') or 'unknown error'
            logger.warning(f"Crawl4AI failed to fetch {url}: {err}")

            # If blocked by anti-bot, use Playwright direct fallback
            is_blocked = "blocked" in err.lower() or "cloudflare" in err.lower() or "challenge" in err.lower()
            if is_blocked:
                logger.info(f"Crawl4AI blocked for {url}, using Playwright direct fallback...")
                content = await self._afetch_with_playwright_fallback(url)
                if content:
                    logger.info(f"Playwright fallback succeeded for {url}")
                    return content
                logger.warning(f"Playwright fallback also returned no content for {url}")

            return ""

    def load(self) -> List[Document]:
        """Load all documents synchronously."""
        return list(self.lazy_load())

    async def aload(self) -> List[Document]:
        """Load all documents asynchronously."""
        return [doc async for doc in self.alazy_load()]

    def lazy_load(self) -> Iterator[Document]:
        """Synchronously load documents from URLs via Crawl4AI."""
        for url in self.urls:
            html_content = asyncio.run(self.afetch_page(url))
            metadata = {"source": url, "backend": "crawl4ai", "output_format": self.output_format}
            yield Document(page_content=html_content, metadata=metadata)

    async def alazy_load(self) -> AsyncIterator[Document]:
        """Asynchronously load documents from URLs via Crawl4AI."""
        for url in self.urls:
            html_content = await self.afetch_page(url)
            metadata = {"source": url, "backend": "crawl4ai", "output_format": self.output_format}
            yield Document(page_content=html_content, metadata=metadata)
