import asyncio
import socket
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from scrapegraphai.docloaders.chromium import ChromiumLoader, _block_unsafe_request
from scrapegraphai.nodes.fetch_node import FetchNode
from scrapegraphai.utils.url_safety import validate_url


@pytest.mark.parametrize(
    "url",
    [
        "http://169.254.169.254/latest/meta-data/iam/security-credentials/",
        "http://2852039166/latest/meta-data/",
        "http://0xa9fea9fe/latest/meta-data/",
        "http://[::ffff:169.254.169.254]/latest/meta-data/",
        "http://[fe80::1]/",
        "http://[fe80::1%25eth0]/",
        "http://[fd00:ec2::254]/latest/meta-data/",
        "http://100.100.100.200/latest/meta-data/",
    ],
)
def test_validate_url_rejects_metadata_addresses(url):
    with pytest.raises(ValueError):
        validate_url(url)


@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1:8000/",
        "http://localhost:11434/",
        "http://192.168.1.10/",
        "https://93.184.216.34/",
        "not a url",
    ],
)
def test_validate_url_allows_other_addresses(url):
    validate_url(url)


def test_validate_url_checks_resolved_address():
    resolved = [(2, 1, 6, "", ("169.254.169.254", 0))]
    with patch("socket.getaddrinfo", return_value=resolved):
        with pytest.raises(ValueError):
            validate_url("http://metadata.example.com/")


def test_validate_url_rejects_if_any_resolved_address_is_blocked():
    resolved = [
        (2, 1, 6, "", ("93.184.216.34", 0)),
        (2, 1, 6, "", ("169.254.169.254", 0)),
    ]
    with patch("socket.getaddrinfo", return_value=resolved):
        with pytest.raises(ValueError):
            validate_url("http://dual.example.com/")


def test_validate_url_ignores_unresolvable_host():
    with patch("socket.getaddrinfo", side_effect=socket.gaierror):
        validate_url("http://does-not-resolve.invalid/")


@pytest.mark.parametrize("use_soup", [True, False])
def test_fetch_node_does_not_fetch_metadata_address(use_soup):
    node = FetchNode(
        input="url",
        output=["doc"],
        node_config={"use_soup": use_soup, "headless": True},
    )
    source = "http://169.254.169.254/latest/meta-data/"
    with (
        patch("scrapegraphai.nodes.fetch_node.requests.get") as get,
        patch("scrapegraphai.nodes.fetch_node.ChromiumLoader") as loader,
    ):
        with pytest.raises(ValueError):
            node.execute({"url": source})
    get.assert_not_called()
    loader.assert_not_called()


class _RedirectHandler(BaseHTTPRequestHandler):
    hits = []

    def do_GET(self):
        self.hits.append(self.path)
        self.send_response(302)
        self.send_header("Location", "http://169.254.169.254/latest/meta-data/")
        self.end_headers()

    def log_message(self, *args):
        pass


def test_fetch_node_does_not_follow_redirect_to_metadata_address():
    _RedirectHandler.hits = []
    server = HTTPServer(("127.0.0.1", 0), _RedirectHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    node = FetchNode(
        input="url",
        output=["doc"],
        node_config={"use_soup": True, "timeout": 2},
    )
    source = f"http://127.0.0.1:{server.server_address[1]}/"
    try:
        with pytest.raises(ValueError):
            node.execute({"url": source})
    finally:
        server.shutdown()
        server.server_close()
    assert _RedirectHandler.hits == ["/"]


@pytest.mark.parametrize(
    "url, blocked",
    [
        ("http://169.254.169.254/latest/meta-data/", True),
        ("http://127.0.0.1:8000/", False),
    ],
)
def test_browser_requests_to_metadata_address_are_aborted(url, blocked):
    route = MagicMock()
    route.request.url = url
    route.abort = AsyncMock()
    route.continue_ = AsyncMock()
    asyncio.run(_block_unsafe_request(route))
    assert route.abort.called is blocked
    assert route.continue_.called is not blocked


def _mock_playwright(page):
    context = MagicMock()
    context.route = AsyncMock()
    context.new_page = AsyncMock(return_value=page)
    browser = MagicMock()
    browser.new_context = AsyncMock(return_value=context)
    browser.close = AsyncMock()
    playwright = MagicMock()
    playwright.chromium.launch = AsyncMock(return_value=browser)
    manager = MagicMock()
    manager.__aenter__ = AsyncMock(return_value=playwright)
    manager.__aexit__ = AsyncMock(return_value=False)
    return manager, context


def _mock_page(url, content="<html>secret</html>"):
    page = MagicMock()
    page.goto = AsyncMock()
    page.url = url
    page.content = AsyncMock(return_value=content)
    page.wait_for_load_state = AsyncMock()
    page.evaluate = AsyncMock(return_value=1000)
    page.mouse.wheel = AsyncMock()
    return page


def _failure_message(manager, method):
    # The scroll loader reports failures as an "Error: ..." string instead of raising
    try:
        result = _run_loader(manager, method)
    except RuntimeError as exc:
        return str(exc)
    assert result.startswith("Error:"), result
    assert "secret" not in result
    return result


def _run_loader(manager, method="ascrape_playwright"):
    loader = ChromiumLoader(["http://example.com/"], retry_limit=1)
    with (
        patch("playwright.async_api.async_playwright", return_value=manager),
        patch("undetected_playwright.Malenia.apply_stealth", new=AsyncMock()),
    ):
        return asyncio.run(getattr(loader, method)("http://example.com/"))


@pytest.mark.parametrize(
    "method",
    [
        "ascrape_playwright",
        "ascrape_playwright_scroll",
        "ascrape_with_js_support",
    ],
)
def test_chromium_loader_rejects_navigation_that_lands_on_metadata_address(method):
    page = _mock_page("http://169.254.169.254/latest/meta-data/")
    manager, _ = _mock_playwright(page)
    assert "metadata" in _failure_message(manager, method)


@pytest.mark.parametrize(
    "method",
    [
        "ascrape_playwright",
        "ascrape_playwright_scroll",
        "ascrape_with_js_support",
    ],
)
def test_chromium_loader_rejects_navigation_after_goto_returned(method):
    page = _mock_page("http://example.com/")

    async def navigate_away():
        page.url = "http://169.254.169.254/latest/meta-data/"
        return "<html>secret</html>"

    page.content = AsyncMock(side_effect=navigate_away)
    manager, _ = _mock_playwright(page)
    assert "metadata" in _failure_message(manager, method)


def test_chromium_loader_registers_request_guard_and_returns_safe_page():
    page = _mock_page("http://example.com/", "<html>ok</html>")
    manager, context = _mock_playwright(page)
    assert _run_loader(manager) == "<html>ok</html>"
    context.route.assert_awaited_once_with("**/*", _block_unsafe_request)
