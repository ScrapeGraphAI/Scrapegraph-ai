import pytest

from scrapegraphai.utils.research_web import (  # Replace with actual path to your file, filter_pdf_links

    search_on_web,
)

def test_google_search():
    """Tests search_on_web with Google search engine."""
    results = search_on_web("test query", search_engine="Google", max_results=2)
    assert len(results) == 2
    # You can further assert if the results actually contain 'test query' in the title/snippet using additional libraries

def test_bing_search():
    """Tests search_on_web with Bing search engine."""
    results = search_on_web("test query", search_engine="Bing", max_results=1)
    assert results is not None
    # You can further assert if the results contain '.com' or '.org' in the domain

def test_invalid_search_engine():
    """Tests search_on_web with invalid search engine."""
    with pytest.raises(ValueError):
        search_on_web("test query", search_engine="Yahoo", max_results=5)

def test_max_results():
    """Tests search_on_web with different max_results values."""
    results_5 = search_on_web("test query", max_results=5)
    results_10 = search_on_web("test query", max_results=10)
    assert len(results_5) <= len(results_10)

def test_filter_pdf_links():
    """Tests the filter_pdf_links function to ensure it removes PDF links."""
    mixed_links = [
        "http://example.com/document.pdf",
        "https://example.org/page.html",
        "http://test.com/file.PDF",
        "https://another.com/index.htm",
    ]
    filtered_links = filter_pdf_links(mixed_links)

    assert len(filtered_links) == 2
    assert "http://example.com/document.pdf" not in filtered_links
    assert "http://test.com/file.PDF" not in filtered_links
    assert "https://example.org/page.html" in filtered_links
    assert "https://another.com/index.htm" in filtered_links