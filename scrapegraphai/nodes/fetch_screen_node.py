"""
fetch_screen_node module
"""
from typing import List, Optional
from playwright.sync_api import sync_playwright
from .base_node import BaseNode
from ..utils.logging import get_logger

class FetchScreenNode(BaseNode):
    """
    FetchScreenNode captures screenshots from a given URL and stores the image data as bytes.
    """

    def __init__(
        self,
        input: str,
        output: List[str],
        node_config: Optional[dict] = None,
        node_name: str = "FetchScreenNode",
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

            viewport_height = page.viewport_size["height"]

            screenshot_counter = 1

            screenshot_data_list = []

            def capture_screenshot(scroll_position, counter):
                page.evaluate(f"window.scrollTo(0, {scroll_position});")
                screenshot_data = page.screenshot()
                screenshot_data_list.append(screenshot_data)

            capture_screenshot(0, screenshot_counter)
            screenshot_counter += 1
            capture_screenshot(viewport_height, screenshot_counter)

            browser.close()

        state["link"] = self.url
        state['screenshots'] = screenshot_data_list

        return state
