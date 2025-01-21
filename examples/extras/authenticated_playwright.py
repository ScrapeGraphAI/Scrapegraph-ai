"""
Example leveraging a state file containing session cookies which
might be leveraged to authenticate to a website and scrape protected
content.
"""

import os
import random

from dotenv import load_dotenv

# import playwright so we can use it to create the state file
from playwright.async_api import async_playwright

from scrapegraphai.graphs import OmniScraperGraph
from scrapegraphai.utils import prettify_exec_info

load_dotenv()

# ************************************************
# Leveraging Playwright external to the invocation of the graph to
# login and create the state file
# ************************************************


# note this is just an example and probably won't actually work on
# LinkedIn, the implementation of the login is highly dependent on the website
async def do_login():
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            timeout=30000,
            headless=False,
            slow_mo=random.uniform(500, 1500),
        )
    page = await browser.new_page()

    # very basic implementation of a login, in reality it may be trickier
    await page.goto("https://www.linkedin.com/login")
    await page.get_by_label("Email or phone").fill("some_bloke@some_domain.com")
    await page.get_by_label("Password").fill("test1234")
    await page.get_by_role("button", name="Sign in").click()
    await page.wait_for_timeout(3000)

    # assuming a successful login, we save the cookies to a file
    await page.context.storage_state(path="./state.json")


async def main():
    await do_login()

    # ************************************************
    # Define the configuration for the graph
    # ************************************************

    openai_api_key = os.getenv("OPENAI_APIKEY")

    graph_config = {
        "llm": {
            "api_key": openai_api_key,
            "model": "openai/gpt-4o",
        },
        "max_images": 10,
        "headless": False,
        # provide the path to the state file
        "storage_state": "./state.json",
    }

    # ************************************************
    # Create the OmniScraperGraph instance and run it
    # ************************************************

    omni_scraper_graph = OmniScraperGraph(
        prompt="List me all the projects with their description.",
        source="https://www.linkedin.com/feed/",
        config=graph_config,
    )

    # the storage_state is used to load the cookies from the state file
    # so we are authenticated and able to scrape protected content
    result = omni_scraper_graph.run()
    print(result)

    # ************************************************
    # Get graph execution info
    # ************************************************

    graph_exec_info = omni_scraper_graph.get_execution_info()
    print(prettify_exec_info(graph_exec_info))


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
