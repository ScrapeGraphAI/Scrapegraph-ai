""" 
Module for minimizing the code
"""
from bs4 import BeautifulSoup
from minify_html import minify
from urllib.parse import urljoin

def cleanup_html(html_content: str, base_url: str) -> str:
    """
    Processes HTML content by removing unnecessary tags, minifying the HTML, and extracting the title and body content.

    Args:
        html_content (str): The HTML content to be processed.

    Returns:
        str: A string combining the parsed title and the minified body content. If no body content is found, it indicates so.

    Example:
        >>> html_content = "<html><head><title>Example</title></head><body><p>Hello World!</p></body></html>"
        >>> remover(html_content)
        'Title: Example, Body: <body><p>Hello World!</p></body>'

    This function is particularly useful for preparing HTML content for environments where bandwidth usage needs to be minimized.
    """

    soup = BeautifulSoup(html_content, 'html.parser')

    # Title Extraction
    title_tag = soup.find('title')
    title = title_tag.get_text() if title_tag else ""

    # Script and Style Tag Removal
    for tag in soup.find_all(['script', 'style']):
        tag.extract()

    # Links extraction
    links = soup.find_all('a')
    link_urls = []
    for link in links:
        if 'href' in link.attrs:
            link_urls.append(urljoin(base_url, link['href']))

    # Body Extraction (if it exists)
    body_content = soup.find('body')
    if body_content:
        # Minify the HTML within the body tag
        minimized_body = minify(str(body_content))
        print("Came here")
        return "Title: " + title + ", Body: " + minimized_body + ", Links: " + str(link_urls)


    print("No Came here")
    return "Title: " + title + ", Body: No body content found" + ", Links: " + str(link_urls)