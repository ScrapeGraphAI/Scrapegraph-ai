""" 
Module for minimizing the code
"""
from bs4 import BeautifulSoup
from minify_html import minify


def remover(html_content: str) -> str:
    """
    This function processes HTML content, removes unnecessary tags, 
    minifies the HTML, and retrieves the title and body content.

    Parameters:
        html_content (str): The HTML content to parse

    Returns:
        str: The parsed title followed by the minified body content
    """

    soup = BeautifulSoup(html_content, 'html.parser')

    # Title Extraction
    title_tag = soup.find('title')
    title = title_tag.get_text() if title_tag else ""

    # Script Tag Removal
    [script.extract() for script in soup.find_all('script')]

    # Body Extraction (if it exists)
    body_content = soup.find('body')
    if body_content:
        # Minify the HTML within the body tag
        minimized_body = minify(str(body_content))
        return "Title: " + title + ", Body: " + minimized_body
    else:
        return "Title: " + title + ", Body: No body content found"
