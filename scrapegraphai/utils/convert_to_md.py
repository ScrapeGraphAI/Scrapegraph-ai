"""
convert_to_md modul
"""
import html2text
import mdformat
from trafilatura import extract


def convert_to_md(html):
    """ Convert HTML to Markdown.
    This function uses the html2text library to convert the provided HTML content to Markdown 
    format.
    The function returns the converted Markdown content as a string.

    Args: html (str): The HTML content to be converted.

    Returns: str: The equivalent Markdown content.

    Example: >>> convert_to_md("<html><body><p>This is a paragraph.</p>
    <h1>This is a heading.</h1></body></html>") 
    'This is a paragraph.\n\n# This is a heading.'

    Note: All the styles and links are ignored during the conversion. """

    return extract(filecontent=html,include_images=True,
                       include_links=True, include_tables=True, output_format="markdown")
