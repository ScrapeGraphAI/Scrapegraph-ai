""" 
Module for minimizing the code
"""
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from minify_html import minify

def cleanup_html(html_content: str, base_url: str) -> str:
    """
    Processes HTML content by removing unnecessary tags, 
    minifying the HTML, and extracting the title and body content.

    Args:
        html_content (str): The HTML content to be processed.

    Returns:
        str: A string combining the parsed title and the minified body content. 
        If no body content is found, it indicates so.

    Example:
        >>> html_content = "<html><head><title>Example</title></head><body><p>Hello World!</p></body></html>"
        >>> remover(html_content)
        'Title: Example, Body: <body><p>Hello World!</p></body>'

    This function is particularly useful for preparing HTML content for 
    environments where bandwidth usage needs to be minimized.
    """

    soup = BeautifulSoup(html_content, 'html.parser')

    title_tag = soup.find('title')
    title = title_tag.get_text() if title_tag else ""

    for tag in soup.find_all(['script', 'style']):
        tag.extract()

    link_urls = [urljoin(base_url, link['href']) for link in soup.find_all('a', href=True)]

    images = soup.find_all('img')
    image_urls = []
    for image in images:
        if 'src' in image.attrs:
            if 'http' not in image['src']:
                image_urls.append(urljoin(base_url, image['src']))
            else:
                image_urls.append(image['src'])

    body_content = soup.find('body')
    if body_content:
        minimized_body = minify(str(body_content))
        return title, minimized_body, link_urls, image_urls

    else:
        raise ValueError(f"""No HTML body content found, please try setting the 'headless'
                         flag to False in the graph configuration. HTML content: {html_content}""")
