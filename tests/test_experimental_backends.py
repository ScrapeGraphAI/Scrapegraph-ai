import pytest
from unittest.mock import patch

from scrapegraphai.experimental import ObscuraLoader, Crawl4aiLoader
from scrapegraphai.nodes.fetch_node import FetchNode


class TestObscuraLoader:
    def test_instantiation_defaults(self):
        loader = ObscuraLoader(["https://example.com"])
        assert loader.cdp_url == "ws://127.0.0.1:9222/devtools/browser"
        assert loader.auto_start is None
        assert loader.proxy is None
        assert len(loader.urls) == 1

    def test_instantiation_with_config(self):
        loader = ObscuraLoader(
            ["https://example.com"],
            cdp_url="ws://127.0.0.1:9333",
            auto_start="docker",
            proxy={"server": "http://proxy:8080"},
            timeout=60,
        )
        assert loader.cdp_url == "ws://127.0.0.1:9333"
        assert loader.auto_start == "docker"
        assert loader.proxy == {"server": "http://proxy:8080"}
        assert loader.timeout == 60

    def test_unknown_auto_start_raises(self):
        loader = ObscuraLoader(["https://example.com"], auto_start="invalid")
        with pytest.raises(ValueError, match="Unknown auto_start mode"):
            loader._ensure_running()

    @pytest.mark.asyncio
    async def test_afetch_page_no_playwright(self):
        loader = ObscuraLoader(["https://example.com"])
        with patch.dict("sys.modules", {"playwright.async_api": None}):
            with pytest.raises(ImportError, match="playwright is required"):
                await loader.afetch_page("https://example.com")


class TestCrawl4aiLoader:
    def test_instantiation_defaults(self):
        loader = Crawl4aiLoader(["https://example.com"])
        assert loader.headless is True
        assert loader.output_format == "markdown"
        assert loader.proxy is None
        assert loader.page_timeout == 60000

    def test_instantiation_with_config(self):
        loader = Crawl4aiLoader(
            ["https://example.com"],
            headless=False,
            output_format="html",
            proxy={"server": "http://proxy:8080"},
            page_timeout=60000,
        )
        assert loader.headless is False
        assert loader.output_format == "html"
        assert loader.proxy == {"server": "http://proxy:8080"}
        assert loader.page_timeout == 60000

    def test_get_content_markdown(self):
        class MockResult:
            markdown = "# Hello"
            html = "<h1>Hello</h1>"
            cleaned_html = "Hello"

        loader = Crawl4aiLoader(["https://example.com"], output_format="markdown")
        assert loader._get_content(MockResult(), "") == "# Hello"

    def test_get_content_html(self):
        class MockResult:
            markdown = "# Hello"
            html = "<h1>Hello</h1>"
            cleaned_html = "Hello"

        loader = Crawl4aiLoader(["https://example.com"], output_format="html")
        assert loader._get_content(MockResult(), "") == "<h1>Hello</h1>"

    def test_get_content_text(self):
        class MockResult:
            markdown = "# Hello"
            html = "<h1>Hello</h1>"
            cleaned_html = "Hello"

        loader = Crawl4aiLoader(["https://example.com"], output_format="text")
        assert loader._get_content(MockResult(), "") == "Hello"


class TestFetchNodeExperimental:
    def test_experimental_config_stored(self):
        fn = FetchNode(
            input="url | local_dir",
            output=["doc"],
            node_config={
                "experimental": {
                    "backend": "obscura",
                    "obscura": {"cdp_url": "ws://127.0.0.1:9222"},
                },
                "headless": True,
            },
        )
        assert fn.experimental == {
            "backend": "obscura",
            "obscura": {"cdp_url": "ws://127.0.0.1:9222"},
        }

    def test_experimental_default_none(self):
        fn = FetchNode(
            input="url | local_dir",
            output=["doc"],
            node_config={"headless": True},
        )
        assert fn.experimental is None

    def test_experimental_unknown_backend(self):
        fn = FetchNode(
            input="url | local_dir",
            output=["doc"],
            node_config={
                "experimental": {"backend": "nonexistent"},
            },
        )
        with pytest.raises(ValueError, match="Unknown experimental backend"):
            fn.execute({"url": "https://example.com"})

    def test_experimental_crawl4ai_backend(self):
        fn = FetchNode(
            input="url | local_dir",
            output=["doc"],
            node_config={
                "experimental": {
                    "backend": "crawl4ai",
                    "crawl4ai": {"output_format": "html"},
                },
                "headless": True,
            },
        )
        assert fn.experimental["backend"] == "crawl4ai"
        assert fn.experimental["crawl4ai"]["output_format"] == "html"
