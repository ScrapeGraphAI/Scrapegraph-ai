import pytest
from bs4 import BeautifulSoup

# Import the functions to be tested
from scrapegraphai.utils.cleanup_html import (
    cleanup_html,
    extract_from_script_tags,
    minify_html,
    reduce_html,
)


def test_extract_from_script_tags():
    """Test extracting JSON and dynamic data from script tags."""
    html = """
    <html>
        <head></head>
        <body>
        <script>var data = {"key": "value"};</script>
        <script>window.globalVar = "hello";</script>
        <script>let ignored = {not:"json"};</script>
        </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")
    result = extract_from_script_tags(soup)
    assert "JSON data from script:" in result
    assert '"key": "value"' in result
    assert 'Dynamic data - globalVar: "hello"' in result


def test_cleanup_html_success():
    """Test cleanup_html with valid HTML containing title, body, links, images, and scripts."""
    html = """
    <html>
        <head>
        <title>Test Title</title>
        </head>
        <body>
        <p>Hello World!</p>
        <a href="/page">Link</a>
        <img src="image.jpg"/>
        <script>var info = {"num": 123};</script>
        </body>
    </html>
    """
    base_url = "http://example.com"
    title, minimized_body, link_urls, image_urls, script_content = cleanup_html(
        html, base_url
    )
    assert title == "Test Title"
    assert "<body>" in minimized_body and "</body>" in minimized_body
    # Check the link is properly joined
    assert "http://example.com/page" in link_urls
    # Check the image is properly joined
    assert "http://example.com/image.jpg" in image_urls
    # Check that we got some output from the script extraction
    assert "JSON data from script" in script_content


def test_cleanup_html_no_body():
    """Test cleanup_html raises ValueError when no <body> tag is present."""
    html = "<html><head><title>No Body</title></head></html>"
    base_url = "http://example.com"
    with pytest.raises(ValueError) as excinfo:
        cleanup_html(html, base_url)
    assert "No HTML body content found" in str(excinfo.value)


def test_minify_html():
    """Test minify_html function to remove comments and unnecessary whitespace."""
    raw_html = """
    <html>
        <!-- this is a comment -->
        <body>
            <p>   Hello   World!   </p>
        </body>
    </html>
    """
    minified = minify_html(raw_html)
    # There should be no comment and no unnecessary spaces between tags
    assert "<!--" not in minified
    assert "  " not in minified


def test_reduce_html_reduction_0():
    """Test reduce_html at reduction level 0 (minification only)."""
    raw_html = """
    <html>
        <body>
            <p>   Some   text   </p>
        </body>
    </html>
    """
    # At reduction level 0, the result equals minify_html(raw_html)
    reduced = reduce_html(raw_html, 0)
    expected = minify_html(raw_html)
    assert reduced == expected


def test_reduce_html_reduction_1():
    """Test reduce_html at reduction level 1 (remove unnecessary attributes and empty style tags)."""
    raw_html = """
    <html>
        <body>
            <div style="color:red" data-extra="should_remove" class="keep">
            <!-- comment should be removed -->
            <p>   Some text   </p>
            </div>
        </body>
    </html>
    """
    reduced = reduce_html(raw_html, 1)
    # Ensure that unwanted attributes are removed (data-extra and style are gone, class remains)
    assert "data-extra" not in reduced
    assert "style=" not in reduced
    assert 'class="keep"' in reduced


def test_reduce_html_reduction_2():
    """Test reduce_html at reduction level 2 (further reducing text content and decomposing style tags)."""
    raw_html = """
    <html>
        <head>
            <style>.unused { color: blue; }</style>
        </head>
        <body>
            <p>   Long text with more than twenty characters. Extra content.   </p>
        </body>
    </html>
    """
    reduced = reduce_html(raw_html, 2)
    # For level 2, text should be truncated to the first 20 characters after normalization.
    # The original text "Long text with more than twenty characters. Extra content."
    # normalized becomes "Long text with more than twenty characters. Extra content."
    # and then truncated to: "Long text with more t" (first 20 characters)
    assert "Long text with more t" in reduced
    # Confirm that style tags contents are completely removed
    assert ".unused" not in reduced


def test_reduce_html_no_body():
    """Test reduce_html returns specific message when no <body> tag is present."""
    raw_html = "<html><head><title>No Body</title></head></html>"
    reduced = reduce_html(raw_html, 2)
    assert reduced == "No <body> tag found in the HTML"
