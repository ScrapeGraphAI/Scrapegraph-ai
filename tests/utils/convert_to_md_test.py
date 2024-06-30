import pytest
from scrapegraphai.utils.convert_to_md import convert_to_md

def test_basic_html_to_md():
    html = "<html><body><p>This is a paragraph.</p><h1>This is a heading.</h1></body></html>"
    assert convert_to_md(html) is not None

def test_html_with_links_and_images():
    html = '<p>This is a <a href="https://example.com">link</a> and this is an <img src="https://example.com/image.jpg" alt="image"></p>'
    assert convert_to_md(html) is  None

def test_html_with_tables():
    html = '''
    <table>
        <tr><th>Header 1</th><th>Header 2</th></tr>
        <tr><td>Row 1, Cell 1</td><td>Row 1, Cell 2</td></tr>
        <tr><td>Row 2, Cell 1</td><td>Row 2, Cell 2</td></tr>
    </table>
    '''
    assert convert_to_md(html) is  None

def test_empty_html():
    html = ""
    assert convert_to_md(html) is None

def test_complex_html_structure():
    html = '''
    <html>
        <body>
            <h1>Main Heading</h1>
            <p>This is a <strong>bold</strong> paragraph with <em>italic</em> text.</p>
            <ul>
                <li>First item</li>
                <li>Second item</li>
                <li>Third item</li>
            </ul>
            <p>Another paragraph with a <a href="https://example.com">link</a>.</p>
        </body>
    </html>
    '''
    assert convert_to_md(html) is not None
