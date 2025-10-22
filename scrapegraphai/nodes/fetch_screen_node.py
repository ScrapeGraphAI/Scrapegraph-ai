"""
fetch_screen_node module
"""

from typing import List, Optional

from playwright.sync_api import sync_playwright

from .base_node import BaseNode


class FetchScreenNode(BaseNode):
    """
    FetchScreenNode captures screenshots from a given URL and stores the image data as bytes.
    """

    def __init__(
        self,
        input: str,
        output: List[str],
        node_config: Optional[dict] = None,
        node_name: str = "FetchScreen",
    ):
        super().__init__(node_name, "node", input, output, 2, node_config)
        self.url = node_config.get("link")

    def execute(self, state: dict) -> dict:
        """
        Captures screenshots from the input URL and stores them in the state dictionary as bytes.
        """
        self.logger.info(f"--- Executing {self.node_name} Node ---")

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(self.url)
            page.wait_for_load_state("networkidle")

            # Get page height
            viewport_height = page.viewport_size["height"]
            page_height = page.evaluate("document.body.scrollHeight")

            screenshot_counter = 1
            screenshot_data_list = []

            def capture_screenshot(scroll_position, counter):
                page.evaluate(f"window.scrollTo(0, {scroll_position});")
                page.wait_for_timeout(500)  # Wait for content to settle
                screenshot_data = page.screenshot()
                screenshot_data_list.append(screenshot_data)

            # Capture entire page by scrolling through it
            scroll_position = 0
            while scroll_position < page_height:
                capture_screenshot(scroll_position, screenshot_counter)
                screenshot_counter += 1
                scroll_position += viewport_height

            # Capture final position if not already captured
            if page_height > viewport_height and scroll_position - viewport_height < page_height:
                capture_screenshot(page_height - viewport_height, screenshot_counter)

            browser.close()

        state["link"] = self.url
        state["screenshots"] = screenshot_data_list

        self.logger.info(f"Captured {len(screenshot_data_list)} screenshots")

        return state
