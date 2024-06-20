"""
convert_to_md modul
"""
import html2text
import mdformat
from trafilatura import extract
from markdownify import markdownify
import pyhtml2md

def convert_to_md(html, provider="local"):
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
    if provider == "openai":
        converter = html2text.HTML2Text()
        formatted = converter.handle(html)
        a = mdformat.text(formatted)
    else:
        a = extract(filecontent=html,include_images=True, include_links=True, include_tables=True, output_format="markdown")
        b = markdownify(html, keep_inline_images_in=['td', 'th', 'a', 'figure'],)
        c = pyhtml2md.convert(html)
    return a
