"""
Experimental: Camoufox stealth browser backend for ScrapeGraphAI.

Camoufox (https://github.com/jo-inc/camofox-browser) is a Firefox fork
with C++-level fingerprint spoofing — patches navigator.hardwareConcurrency,
WebGL renderers, AudioContext, screen geometry, and WebRTC before JavaScript
ever sees them. Bypasses Google, Cloudflare, and most bot detection.

This loader starts the camofox-browser REST API server as a subprocess
(via npx), then uses its REST API to create tabs, evaluate JS to extract
HTML content, and clean up.

Usage in node_config:
    "experimental": {
        "backend": "camoufox",
        "camoufox": {
            "headless": true,
            "timeout": 30,
            "port": 9377
        }
    }
"""

from __future__ import annotations

import asyncio
import os
import subprocess
import time
from typing import Any, AsyncIterator, Iterator, List, Optional
from urllib.parse import urljoin

from ..utils import get_logger

logger = get_logger("camoufox-loader")

DEFAULT_CAMOFOX_PORT = 9377
CAMOFOX_BASE_URL = "http://127.0.0.1:{}"


class CamoufoxLoader:
    """
    Fetches web pages using Camoufox stealth browser via its REST API.

    Camoufox is a Firefox fork with C++-level anti-detection patches
    that bypass Cloudflare, Google, and most bot detection systems.

    Supports auto-start via npx (requires Node.js + npm).
    """

    def __init__(
        self,
        urls: List[str],
        *,
        headless: bool = True,
        timeout: int = 30,
        port: int = DEFAULT_CAMOFOX_PORT,
        auto_start: bool = True,
        proxy: Optional[dict] = None,
        **kwargs: Any,
    ):
        self.urls = urls
        self.headless = headless
        self.timeout = timeout
        self.port = port
        self.auto_start = auto_start
        self.proxy = proxy
        self.browser_config = kwargs
        self._process = None
        self._base_url = CAMOFOX_BASE_URL.format(port)

    def _check_npx(self) -> bool:
        """Check if npx (Node.js) is available."""
        try:
            result = subprocess.run(
                "npx --version",
                capture_output=True, timeout=10, check=False, shell=True,
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _start_server(self):
        """Start camofox-browser server via npx."""
        logger.info("Starting Camoufox server via npx...")

        if not self._check_npx():
            raise RuntimeError(
                "npx (Node.js) not found. Install Node.js from https://nodejs.org/"
            )

        env = os.environ.copy()
        env["CAMOFOX_PORT"] = str(self.port)
        if not self.headless:
            env["CAMOFOX_HEADLESS"] = "false"

        self._process = subprocess.Popen(
            f"npx @askjo/camofox-browser",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=env, shell=True,
        )
        logger.info("Waiting for Camoufox server to start...")
        time.sleep(5)

    def _ensure_running(self):
        """Ensure the Camoufox server is running."""
        if self.auto_start and self._process is None:
            # Check if already running on the port
            if not self._is_server_ready():
                self._start_server()
        if not self._is_server_ready():
            if self.auto_start:
                logger.info("Camoufox server not ready, retrying start...")
                self._start_server()
            else:
                raise RuntimeError(
                    f"Camoufox server not running on port {self.port}. "
                    f"Start it manually: npx @askjo/camofox-browser"
                )

    def _is_server_ready(self) -> bool:
        """Check if the Camoufox server health endpoint responds."""
        import urllib.request
        import urllib.error
        try:
            resp = urllib.request.urlopen(
                f"{self._base_url}/health",
                timeout=3,
            )
            return resp.status == 200
        except Exception:
            return False

    def _wait_for_server(self, max_retries: int = 15) -> bool:
        """Wait for server to become healthy."""
        for i in range(max_retries):
            if self._is_server_ready():
                logger.info(f"Camoufox server ready after ~{(i+1)*2}s")
                return True
            time.sleep(2)
        return False

    def _cleanup(self):
        """Clean up the subprocess."""
        if self._process is not None:
            logger.info("Shutting down Camoufox server...")
            try:
                import urllib.request
                req = urllib.request.Request(
                    f"{self._base_url}/stop",
                    method="POST",
                    data=b'{}',
                )
                urllib.request.urlopen(req, timeout=5)
            except Exception:
                pass
            self._process.terminate()
            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._process.kill()
            self._process = None

    async def _api_request(self, method: str, path: str, body: Optional[dict] = None) -> dict:
        """Make an async HTTP request to the Camoufox REST API."""
        import aiohttp
        url = urljoin(self._base_url, path)
        async with aiohttp.ClientSession() as session:
            kwargs: dict[str, Any] = {}
            if body is not None:
                kwargs["json"] = body
            async with session.request(method, url, timeout=aiohttp.ClientTimeout(total=self.timeout), **kwargs) as resp:
                if resp.status >= 400:
                    text = await resp.text()
                    raise RuntimeError(f"Camoufox API error {resp.status}: {text[:200]}")
                content_type = resp.content_type or ""
                if "json" in content_type:
                    return await resp.json()
                text = await resp.text()
                return {"text": text}

    async def _async_start_server(self):
        """Start camofox-browser server via npx (async-safe)."""
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._start_server)

    async def _async_wait_for_server(self, max_retries: int = 15) -> bool:
        """Wait for server to become healthy (async-safe)."""
        for i in range(max_retries):
            if self._is_server_ready():
                logger.info(f"Camoufox server ready after ~{(i+1)*2}s")
                return True
            await asyncio.sleep(2)
        return False

    async def _async_ensure_running(self):
        """Ensure the Camoufox server is running (async-safe)."""
        if self.auto_start and self._process is None:
            if not self._is_server_ready():
                await self._async_start_server()
        if not self._is_server_ready():
            if self.auto_start:
                logger.info("Camoufox server not ready, retrying start...")
                await self._async_start_server()
            else:
                raise RuntimeError(
                    f"Camoufox server not running on port {self.port}. "
                    f"Start it manually: npx @askjo/camofox-browser"
                )

    async def _async_cleanup(self):
        """Clean up the subprocess (async-safe)."""
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._cleanup)

    async def afetch_page(self, url: str) -> str:
        """
        Fetch a page via Camoufox stealth browser.

        1. Create a tab with the URL
        2. Evaluate JS to extract document.documentElement.outerHTML
        3. Close the tab
        """
        logger.info(f"Fetching via Camoufox: {url}")
        await self._async_ensure_running()

        if not self._is_server_ready():
            if not await self._async_wait_for_server():
                raise RuntimeError(
                    f"Camoufox server on port {self.port} did not become ready"
                )

        import aiohttp

        try:
            response = await self._api_request("POST", "/tabs", {
                "userId": "scrapegraphai",
                "sessionKey": "default",
                "url": url,
            })
        except (aiohttp.ClientError, Exception) as exc:
            if self.auto_start:
                logger.warning(f"Camoufox request failed: {exc}. Restarting...")
                await self._async_cleanup()
                await self._async_start_server()
                if not await self._async_wait_for_server():
                    raise RuntimeError("Camoufox server failed to restart")
                response = await self._api_request("POST", "/tabs", {
                    "userId": "scrapegraphai",
                    "sessionKey": "default",
                    "url": url,
                })
            else:
                raise

        tab_id = response.get("tabId")
        if not tab_id:
            raise RuntimeError(f"Camoufox did not return tabId: {response}")

        try:
            evaluate_response = await self._api_request("POST", f"/tabs/{tab_id}/evaluate", {
                "userId": "scrapegraphai",
                "expression": "document.documentElement.outerHTML",
            })

            content = evaluate_response.get("result", "")
            if not content:
                snapshot_response = await self._api_request("GET", f"/tabs/{tab_id}/snapshot?userId=scrapegraphai")
                content = snapshot_response.get("snapshot", "")

            return content

        finally:
            try:
                await self._api_request("DELETE", f"/tabs/{tab_id}?userId=scrapegraphai")
            except Exception:
                pass

    def load(self) -> list:
        """Synchronously load all documents."""
        return list(self.lazy_load())

    def lazy_load(self) -> Iterator[Document]:
        """Synchronously load documents from URLs via Camoufox."""
        from langchain_core.documents import Document
        try:
            for url in self.urls:
                html_content = asyncio.run(self.afetch_page(url))
                metadata = {"source": url, "backend": "camoufox"}
                yield Document(page_content=html_content, metadata=metadata)
        finally:
            self._cleanup()

    async def alazy_load(self) -> AsyncIterator[Document]:
        """Asynchronously load documents from URLs via Camoufox."""
        from langchain_core.documents import Document
        try:
            for url in self.urls:
                html_content = await self.afetch_page(url)
                metadata = {"source": url, "backend": "camoufox"}
                yield Document(page_content=html_content, metadata=metadata)
        finally:
            self._cleanup()
