"""
browserbase integration module 
"""
from typing import List

def browser_base_fetch(api_key: str, project_id: str, link: List[str], text_content: bool = True, async_mode: bool = False) -> List[str]:
    """
    BrowserBase Fetch

    This module provides an interface to the BrowserBase API.

    The `browser_base_fetch` function takes three arguments:
    - `api_key`: The API key provided by BrowserBase.
    - `project_id`: The ID of the project on BrowserBase where you want to fetch data from.
    - `link`: The URL or link that you want to fetch data from.
    - `text_content`: A boolean flag to specify whether to return only the text content (True) or the full HTML (False).
    - `async_mode`: A boolean flag that determines whether the function runs asynchronously (True) or synchronously (False, default).

    It initializes a Browserbase object with the given API key and project ID, 
    then uses this object to load the specified link. 
    It returns the result of the loading operation.

    Example usage:

    ```
    from browser_base_fetch import browser_base_fetch

    result = browser_base_fetch(api_key="your_api_key", 
    project_id="your_project_id", link="https://example.com")
    print(result)
    ```

    Please note that you need to replace "your_api_key" and "your_project_id" 
    with your actual BrowserBase API key and project ID.

    Args:
        api_key (str): The API key provided by BrowserBase.
        project_id (str): The ID of the project on BrowserBase where you want to fetch data from.
        link (str): The URL or link that you want to fetch data from.
        text_content (bool): Whether to return only the text content (True) or the full HTML (False). Defaults to True.
        async_mode (bool): Whether to run the function asynchronously (True) or synchronously (False). Defaults to False.

    Returns:
        object: The result of the loading operation.
    """

    try:
        from browserbase import Browserbase
    except ImportError:
        raise ImportError("The browserbase module is not installed. Please install it using `pip install browserbase`.")


    browserbase = Browserbase(api_key=api_key, project_id=project_id)

    result = []
    async def _async_fetch_link(l):
        return await asyncio.to_thread(browserbase.load, l, text_content=text_content)

    if async_mode:
        async def _async_browser_base_fetch():
            for l in link:
                result.append(await _async_fetch_link(l))
            return result

        result = asyncio.run(_async_browser_base_fetch())
    else:
        for l in link:
            result.append(browserbase.load(l, text_content=text_content))


    return result
