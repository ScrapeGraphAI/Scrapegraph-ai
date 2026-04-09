"""
PlasmateLoader — lightweight page fetcher using Plasmate (https://github.com/plasmate-labs/plasmate).

Plasmate is an open-source Rust browser engine that outputs a Structured Object Model (SOM)
instead of raw HTML. It requires no Chrome process, uses ~64MB RAM per session vs ~300MB,
and delivers 10-100x fewer tokens per page — lowering LLM costs for AI-powered scraping.

Install: pip install plasmate
Docs:    https://plasmate.app
"""

import asyncio
import subprocess
import shutil
from typing import AsyncIterator, Iterator, List, Optional

from langchain_community.document_loaders.base import BaseLoader
from langchain_core.documents import Document

from ..utils import get_logger

logger = get_logger("plasmate-loader")

_INSTALL_MSG = (
    "plasmate is required for PlasmateLoader. "
    "Install it with: pip install plasmate\n"
    "Docs: https://plasmate.app"
)


def _check_plasmate() -> str:
    """Return the path to the plasmate binary, or raise ImportError."""
    path = shutil.which("plasmate")
    if path is None:
        # Also check the Python-installed entry point location
        try:
            import plasmate as _p  # noqa: F401
            path = shutil.which("plasmate")
        except ImportError:
            pass
    if path is None:
        raise ImportError(_INSTALL_MSG)
    return path


class PlasmateLoader(BaseLoader):
    """Fetches pages using Plasmate — a lightweight Rust browser engine that outputs
    Structured Object Model (SOM) instead of raw HTML.

    Advantages over ChromiumLoader for static / server-rendered pages:
    - No Chrome/Playwright required — single binary, installs via pip
    - ~64MB RAM per session vs ~300MB for Chromium
    - 10-100x fewer tokens per page (SOM strips nav, ads, boilerplate)
    - Drops into existing ScrapeGraphAI workflows with minimal config changes

    For SPAs or pages that require JavaScript rendering, set ``fallback_to_chrome=True``
    to automatically retry with ChromiumLoader on empty or error responses.

    Attributes:
        urls: List of URLs to fetch.
        output_format: Plasmate output format — ``"text"`` (default, most compatible),
            ``"som"`` (full JSON), or ``"markdown"``.
        timeout: Per-request timeout in seconds. Defaults to 30.
        selector: Optional ARIA role or CSS id selector to scope extraction
            (e.g. ``"main"`` or ``"#content"``).
        extra_headers: Optional dict of HTTP headers to pass to each request.
        fallback_to_chrome: If True, retry with ChromiumLoader when Plasmate
            returns empty content (useful for JS-heavy SPAs). Defaults to False.
        chrome_kwargs: Extra kwargs forwarded to ChromiumLoader when fallback is used.

    Example::

        from scrapegraphai.docloaders import PlasmateLoader

        loader = PlasmateLoader(
            urls=["https://docs.python.org/3/library/json.html"],
            output_format="text",
            timeout=30,
        )
        docs = loader.load()
        print(docs[0].page_content[:500])
    """

    def __init__(
        self,
        urls: List[str],
        *,
        output_format: str = "text",
        timeout: int = 30,
        selector: Optional[str] = None,
        extra_headers: Optional[dict] = None,
        fallback_to_chrome: bool = False,
        **chrome_kwargs,
    ):
        if output_format not in ("som", "text", "markdown", "links"):
            raise ValueError(
                f"output_format must be one of 'som', 'text', 'markdown', 'links'; got {output_format!r}"
            )
        self.urls = urls
        self.output_format = output_format
        self.timeout = timeout
        self.selector = selector
        self.extra_headers = extra_headers or {}
        self.fallback_to_chrome = fallback_to_chrome
        self.chrome_kwargs = chrome_kwargs

    def _build_cmd(self, url: str) -> List[str]:
        """Build the plasmate CLI command for a given URL."""
        cmd = [
            "plasmate", "fetch", url,
            "--format", self.output_format,
            "--timeout", str(self.timeout * 1000),  # plasmate uses milliseconds
        ]
        if self.selector:
            cmd += ["--selector", self.selector]
        for key, value in self.extra_headers.items():
            cmd += ["--header", f"{key}: {value}"]
        return cmd

    def _fetch_url(self, url: str) -> str:
        """Synchronously fetch a URL via the plasmate binary."""
        binary = _check_plasmate()
        cmd = self._build_cmd(url)
        cmd[0] = binary  # use resolved path

        logger.info(f"[PlasmateLoader] Fetching: {url}")
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout + 5,  # outer kill timeout slightly above plasmate's
            )
            if result.returncode != 0:
                logger.warning(
                    f"[PlasmateLoader] plasmate exited {result.returncode} for {url}: {result.stderr[:200]}"
                )
                return ""
            content = result.stdout.strip()
            logger.info(f"[PlasmateLoader] Got {len(content)} chars from {url}")
            return content
        except subprocess.TimeoutExpired:
            logger.warning(f"[PlasmateLoader] Timeout fetching {url}")
            return ""
        except FileNotFoundError:
            raise ImportError(_INSTALL_MSG)

    def _fallback_fetch(self, url: str) -> str:
        """Fall back to ChromiumLoader when Plasmate returns empty content."""
        from .chromium import ChromiumLoader

        logger.info(f"[PlasmateLoader] Falling back to ChromiumLoader for: {url}")
        loader = ChromiumLoader([url], **self.chrome_kwargs)
        docs = loader.load()
        return docs[0].page_content if docs else ""

    def lazy_load(self) -> Iterator[Document]:
        """Yield Documents one at a time, fetching each URL synchronously."""
        for url in self.urls:
            content = self._fetch_url(url)

            if not content.strip() and self.fallback_to_chrome:
                content = self._fallback_fetch(url)

            if not content.strip():
                logger.warning(f"[PlasmateLoader] Empty content for {url} — skipping")
                continue

            yield Document(
                page_content=content,
                metadata={
                    "source": url,
                    "loader": "plasmate",
                    "format": self.output_format,
                },
            )

    async def _async_fetch_url(self, url: str) -> str:
        """Asynchronously fetch a URL by running the plasmate binary in a thread pool."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._fetch_url, url)

    async def alazy_load(self) -> AsyncIterator[Document]:
        """Asynchronously yield Documents, fetching all URLs concurrently."""
        tasks = [self._async_fetch_url(url) for url in self.urls]
        results = await asyncio.gather(*tasks)

        for url, content in zip(self.urls, results):
            if not content.strip() and self.fallback_to_chrome:
                content = self._fallback_fetch(url)

            if not content.strip():
                logger.warning(f"[PlasmateLoader] Empty content for {url} — skipping")
                continue

            yield Document(
                page_content=content,
                metadata={
                    "source": url,
                    "loader": "plasmate",
                    "format": self.output_format,
                },
            )
