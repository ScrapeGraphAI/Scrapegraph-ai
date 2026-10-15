from langchain_core.documents import Document

from scrapegraphai.nodes import ParseNode


def _url_parse_node():
    return ParseNode(
        input="doc & (url | local_dir)",
        output=["parsed_doc", "link_urls", "img_urls"],
        node_config={"chunk_size": 4096, "parse_urls": True, "llm_model": None},
    )


def test_extract_urls_keeps_absolute_urls_intact():
    text = (
        "Read the [guide](https://docs.example.org/guide/start), "
        "the [about page](/about) and https://www.other.com/page?x=1\n"
        "![logo](https://cdn.example.net/img/logo.png) ![hero](/static/hero.jpg)"
    )

    links, images = _url_parse_node()._extract_urls(
        text, "https://example.com/blog/post"
    )

    assert set(links) == {
        "https://docs.example.org/guide/start",
        "https://www.other.com/page?x=1",
        "https://example.com/about",
    }
    assert set(images) == {
        "https://cdn.example.net/img/logo.png",
        "https://example.com/static/hero.jpg",
    }


def test_extract_urls_from_local_source_keeps_absolute_urls():
    text = (
        "[guide](https://docs.example.org/guide) ![logo](http://cdn.example.net/a.png)"
    )

    links, images = _url_parse_node()._extract_urls(text, "<html>local</html>")

    assert links == ["https://docs.example.org/guide"]
    assert images == ["http://cdn.example.net/a.png"]


def test_execute_returns_absolute_links_unchanged():
    html = (
        "<html><body><p>Docs: <a href='https://docs.example.org/guide'>guide</a>"
        " <a href='/about'>about</a></p></body></html>"
    )
    state = {
        "doc": [Document(page_content=html)],
        "url": "https://example.com/blog/post",
    }

    state = _url_parse_node().execute(state)

    assert set(state["link_urls"]) == {
        "https://docs.example.org/guide",
        "https://example.com/about",
    }
