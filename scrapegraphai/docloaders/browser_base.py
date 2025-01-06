"""
browserbase integration module
"""

import asyncio
from typing import List


def browser_base_fetch(
    api_key: str,
    project_id: str,
    link: List[str],
    text_content: bool = True,
    async_mode: bool = False,
) -> List[str]:
    """
    BrowserBase Fetch

    This module provides an interface to the BrowserBase API.

    Args:
        api_key (str): The API key provided by BrowserBase.
        project_id (str): The ID of the project on BrowserBase where you want to fetch data from.
        link (List[str]): The URLs or links that you want to fetch data from.
        text_content (bool): Whether to return only the text content (True) or the full HTML (False).
        async_mode (bool): Whether to run the function asynchronously (True) or synchronously (False).

    Returns:
        List[str]: The results of the loading operations.
    """
    try:
        from browserbase import Browserbase
    except ImportError:
        raise ImportError(
            "The browserbase module is not installed. Please install it using `pip install browserbase`."
        )

    # Initialize client with API key
    browserbase = Browserbase(api_key=api_key)

    # Create session with project ID
    session = browserbase.sessions.create(project_id=project_id)

    result = []

    async def _async_fetch_link(url):
        return await asyncio.to_thread(session.load, url, text_content=text_content)

    if async_mode:

        async def _async_browser_base_fetch():
            for url in link:
                result.append(await _async_fetch_link(url))
            return result

        result = asyncio.run(_async_browser_base_fetch())
    else:
        for url in link:
            result.append(session.load(url, text_content=text_content))

    return result
