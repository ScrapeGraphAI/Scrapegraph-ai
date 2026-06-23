import pytest
import requests

pytestmark = pytest.mark.e2e

TEST_URL = "https://example.com"


class TestCrawl4aiLoaderE2E:
    def test_fetch_real_url_content(self):
        from scrapegraphai.experimental import Crawl4aiLoader

        loader = Crawl4aiLoader([TEST_URL], output_format="markdown", headless=True)
        docs = loader.load()

        assert len(docs) == 1
        assert "Example Domain" in docs[0].page_content
        assert docs[0].metadata["source"] == TEST_URL
        assert docs[0].metadata["backend"] == "crawl4ai"

    def test_fetch_real_url_html_format(self):
        from scrapegraphai.experimental import Crawl4aiLoader

        loader = Crawl4aiLoader([TEST_URL], output_format="html", headless=True)
        docs = loader.load()

        assert len(docs) == 1
        assert "<h1>" in docs[0].page_content or "Example Domain" in docs[0].page_content

    def test_fetch_real_url_text_format(self):
        from scrapegraphai.experimental import Crawl4aiLoader

        loader = Crawl4aiLoader([TEST_URL], output_format="text", headless=True)
        docs = loader.load()

        assert len(docs) == 1
        assert "Example Domain" in docs[0].page_content


class TestObscuraLoaderE2E:
    def test_connection_refused_when_not_running(self):
        from scrapegraphai.experimental import ObscuraLoader

        loader = ObscuraLoader(
            [TEST_URL],
            cdp_url="ws://127.0.0.1:29999/devtools/browser",
            auto_start=None,
        )
        with pytest.raises((ConnectionRefusedError, OSError, Exception)):
            import asyncio
            asyncio.run(loader.afetch_page(TEST_URL))


class TestFetchNodeE2E:
    def test_fetch_node_with_crawl4ai_backend(self):
        from scrapegraphai.nodes.fetch_node import FetchNode

        fn = FetchNode(
            input="url | local_dir",
            output=["doc"],
            node_config={
                "experimental": {
                    "backend": "crawl4ai",
                    "crawl4ai": {"output_format": "markdown"},
                },
                "headless": True,
            },
        )
        result = fn.execute({"url": TEST_URL})
        assert "doc" in result
        content = result["doc"].page_content if hasattr(result["doc"], "page_content") else str(result["doc"])
        assert "Example Domain" in content

    def test_fetch_node_playwright_fallback(self):
        from scrapegraphai.nodes.fetch_node import FetchNode

        fn = FetchNode(
            input="url | local_dir",
            output=["doc"],
            node_config={"headless": True},
        )
        result = fn.execute({"url": TEST_URL})
        assert "doc" in result
