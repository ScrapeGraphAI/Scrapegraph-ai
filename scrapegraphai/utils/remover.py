"""
Module for removing the unused html tags
"""
from bs4 import BeautifulSoup


def remover(html_content: str) -> str:
    """
    This function processes the HTML content, removes unnecessary tags,
     and retrieves the title and body content.

    Parameters:
        html_content (str): the HTML content to parse

    Returns:
        str: the parsed title followed by the body content without script tags
    """

    soup = BeautifulSoup(html_content, 'html.parser')

    # Estrai il titolo
    title_tag = soup.find('title')
    title = title_tag.get_text() if title_tag else ""

    # Rimuovi i tag <script> in tutto il documento
    [script.extract() for script in soup.find_all('script')]

    # Estrai il corpo del documento
    body_content = soup.find('body')
    body = str(body_content) if body_content else ""

    return title + body
