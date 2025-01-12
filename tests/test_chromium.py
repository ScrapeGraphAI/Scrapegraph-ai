import asyncio
import pytest
import time

from langchain_core.documents import Document
from scrapegraphai.docloaders.chromium import ChromiumLoader
from scrapegraphai.utils import Proxy
from unittest.mock import AsyncMock, MagicMock, patch

class TestChromiumLoader:
    @pytest.mark.asyncio
    async def test_scrape_with_js_support(self):
        # Arrange
        url = "https://example.com"
        expected_content = "<html><body>JavaScript rendered content</body></html>"

        # Mock the playwright and its components
        with patch("playwright.async_api.async_playwright") as mock_playwright:
            # Set up the mock chain
            mock_browser = AsyncMock()
            mock_context = AsyncMock()
            mock_page = AsyncMock()

            mock_playwright.return_value.__aenter__.return_value.chromium.launch.return_value = mock_browser
            mock_browser.new_context.return_value = mock_context
            mock_context.new_page.return_value = mock_page
            mock_page.content.return_value = expected_content

            # Create the ChromiumLoader instance
            loader = ChromiumLoader([url], requires_js_support=True)

            # Act
            documents = [doc async for doc in loader.alazy_load()]

            # Assert
            assert len(documents) == 1
            assert documents[0].page_content == expected_content
            assert documents[0].metadata["source"] == url

            # Verify that the correct methods were called
            mock_page.goto.assert_called_once_with(url, wait_until="networkidle")
            mock_page.content.assert_called_once()

    @pytest.mark.asyncio
    async def test_ascrape_playwright_scroll(self):
        # Arrange
        url = "https://example.com"
        expected_content = "<html><body>Scrolled content</body></html>"

        # Mock the playwright and its components
        with patch("playwright.async_api.async_playwright") as mock_playwright, \
             patch("undetected_playwright.Malenia") as mock_malenia, \
             patch("time.sleep", return_value=None) as mock_sleep:

            # Set up the mock chain
            mock_browser = AsyncMock()
            mock_context = AsyncMock()
            mock_page = AsyncMock()

            mock_playwright.return_value.__aenter__.return_value.chromium.launch.return_value = mock_browser
            mock_browser.new_context.return_value = mock_context
            mock_context.new_page.return_value = mock_page

            # Mock the page methods
            mock_page.evaluate.side_effect = [1000, 2000, 2000]  # Simulate scrolling
            mock_page.content.return_value = expected_content

            # Create the ChromiumLoader instance
            loader = ChromiumLoader([url])

            # Act
            result = await loader.ascrape_playwright_scroll(url, timeout=10, scroll=5000, sleep=1)

            # Assert
            assert result == expected_content

            # Verify that the correct methods were called
            mock_page.goto.assert_called_once_with(url, wait_until="domcontentloaded")
            mock_page.wait_for_load_state.assert_called_once()
            assert mock_page.evaluate.call_count == 3  # Called for each scroll attempt
            mock_page.mouse.wheel.assert_called_with(0, 5000)
            mock_sleep.assert_called_with(1)
            mock_page.content.assert_called_once()
            mock_browser.close.assert_awaited_once()

            # Verify that Malenia.apply_stealth was called
            mock_malenia.apply_stealth.assert_called_once_with(mock_context)

    def test_lazy_load(self):
        # Arrange
        urls = ["https://example1.com", "https://example2.com"]
        expected_content = "<html><body>Test content</body></html>"

        # Mock the ascrape_playwright method
        with patch.object(ChromiumLoader, 'ascrape_playwright', new_callable=AsyncMock) as mock_scrape:
            mock_scrape.return_value = expected_content

            # Create the ChromiumLoader instance
            loader = ChromiumLoader(urls)

            # Act
            documents = list(loader.lazy_load())

            # Assert
            assert len(documents) == 2
            for i, doc in enumerate(documents):
                assert isinstance(doc, Document)
                assert doc.page_content == expected_content
                assert doc.metadata["source"] == urls[i]

            # Verify that the mocked method was called for each URL
            assert mock_scrape.call_count == 2
            mock_scrape.assert_any_call(urls[0])
            mock_scrape.assert_any_call(urls[1])

    @pytest.mark.asyncio
    async def test_ascrape_undetected_chromedriver(self):
        # Arrange
        url = "https://example.com"
        expected_content = "<html><body>Selenium scraped content</body></html>"

        # Mock undetected_chromedriver and Selenium components
        with patch("undetected_chromedriver.Chrome") as mock_chrome, \
             patch("selenium.webdriver.chrome.options.Options") as mock_options:

            # Set up the mock chain
            mock_driver = MagicMock()
            mock_driver.page_source = expected_content
            mock_chrome.return_value = mock_driver

            # Create the ChromiumLoader instance
            loader = ChromiumLoader([url], backend="selenium", browser_name="chromium")

            # Act
            result = await loader.ascrape_undetected_chromedriver(url)

            # Assert
            assert result == expected_content

            # Verify that the correct methods were called
            mock_options.assert_called_once()
            mock_chrome.assert_called_once()
            mock_driver.get.assert_called_once_with(url)
            mock_driver.quit.assert_called_once()

    @pytest.mark.asyncio
    async def test_ascrape_playwright_with_firefox(self):
        # Arrange
        url = "https://example.com"
        expected_content = "<html><body>Firefox scraped content</body></html>"

        # Mock the playwright and its components
        with patch("playwright.async_api.async_playwright") as mock_playwright, \
             patch("undetected_playwright.Malenia") as mock_malenia:

            # Set up the mock chain
            mock_browser = AsyncMock()
            mock_context = AsyncMock()
            mock_page = AsyncMock()

            mock_playwright.return_value.__aenter__.return_value.firefox.launch.return_value = mock_browser
            mock_browser.new_context.return_value = mock_context
            mock_context.new_page.return_value = mock_page
            mock_page.content.return_value = expected_content

            # Create the ChromiumLoader instance with Firefox
            loader = ChromiumLoader([url], browser_name="firefox")

            # Act
            result = await loader.ascrape_playwright(url, browser_name="firefox")

            # Assert
            assert result == expected_content

            # Verify that the correct methods were called
            mock_playwright.return_value.__aenter__.return_value.firefox.launch.assert_called_once()
            mock_browser.new_context.assert_called_once()
            mock_context.new_page.assert_called_once()
            mock_page.goto.assert_called_once_with(url, wait_until="domcontentloaded")
            mock_page.wait_for_load_state.assert_called_once()
            mock_page.content.assert_called_once()
            mock_browser.close.assert_awaited_once()

            # Verify that Malenia.apply_stealth was called
            mock_malenia.apply_stealth.assert_called_once_with(mock_context)

    @pytest.mark.asyncio
    async def test_ascrape_playwright_scroll_to_bottom(self):
        # Arrange
        url = "https://example.com"
        expected_content = "<html><body>Scrolled to bottom content</body></html>"

        # Mock the playwright and its components
        with patch("playwright.async_api.async_playwright") as mock_playwright, \
             patch("undetected_playwright.Malenia") as mock_malenia, \
             patch("time.sleep", return_value=None) as mock_sleep, \
             patch("time.time", side_effect=[0, 5, 10, 15]):  # Simulate time passing

            # Set up the mock chain
            mock_browser = AsyncMock()
            mock_context = AsyncMock()
            mock_page = AsyncMock()

            mock_playwright.return_value.__aenter__.return_value.chromium.launch.return_value = mock_browser
            mock_browser.new_context.return_value = mock_context
            mock_context.new_page.return_value = mock_page

            # Mock the page methods
            mock_page.evaluate.side_effect = [1000, 2000, 3000, 3000]  # Simulate scrolling until bottom
            mock_page.content.return_value = expected_content

            # Create the ChromiumLoader instance
            loader = ChromiumLoader([url])

            # Act
            result = await loader.ascrape_playwright_scroll(url, timeout=30, scroll=15000, sleep=2, scroll_to_bottom=True)

            # Assert
            assert result == expected_content

            # Verify that the correct methods were called
            mock_page.goto.assert_called_once_with(url, wait_until="domcontentloaded")
            mock_page.wait_for_load_state.assert_called_once()
            assert mock_page.evaluate.call_count == 4  # Called for each scroll attempt
            assert mock_page.mouse.wheel.call_count == 3  # Called until bottom is reached
            mock_page.mouse.wheel.assert_called_with(0, 15000)
            assert mock_sleep.call_count == 3  # Called after each scroll
            mock_page.content.assert_called_once()
            mock_browser.close.assert_awaited_once()

            # Verify that Malenia.apply_stealth was called
            mock_malenia.apply_stealth.assert_called_once_with(mock_context)

    @pytest.mark.asyncio
    async def test_chromium_loader_with_custom_proxy(self):
        # Arrange
        url = "https://example.com"
        expected_content = "<html><body>Proxied content</body></html>"
        custom_proxy = Proxy(
            server="http://proxy.example.com:8080",
            username="user",
            password="pass"
        )

        with patch("scrapegraphai.docloaders.chromium.parse_or_search_proxy") as mock_parse_proxy, \
             patch("playwright.async_api.async_playwright") as mock_playwright, \
             patch("undetected_playwright.Malenia") as mock_malenia:

            # Set up the mock chain
            mock_parse_proxy.return_value = custom_proxy
            mock_browser = AsyncMock()
            mock_context = AsyncMock()
            mock_page = AsyncMock()

            mock_playwright.return_value.__aenter__.return_value.chromium.launch.return_value = mock_browser
            mock_browser.new_context.return_value = mock_context
            mock_context.new_page.return_value = mock_page
            mock_page.content.return_value = expected_content

            # Create the ChromiumLoader instance with custom proxy
            loader = ChromiumLoader([url], proxy=custom_proxy)

            # Act
            result = await loader.ascrape_playwright(url)

            # Assert
            assert result == expected_content

            # Verify that the proxy was correctly parsed and used
            mock_parse_proxy.assert_called_once_with(custom_proxy)
            mock_playwright.return_value.__aenter__.return_value.chromium.launch.assert_called_once_with(
                headless=True,
                proxy={
                    "server": "http://proxy.example.com:8080",
                    "username": "user",
                    "password": "pass"
                }
            )

            # Verify other method calls
            mock_browser.new_context.assert_called_once()
            mock_context.new_page.assert_called_once()
            mock_page.goto.assert_called_once_with(url, wait_until="domcontentloaded")
            mock_page.wait_for_load_state.assert_called_once()
            mock_page.content.assert_called_once()
            mock_browser.close.assert_awaited_once()

            # Verify that Malenia.apply_stealth was called
            mock_malenia.apply_stealth.assert_called_once_with(mock_context)