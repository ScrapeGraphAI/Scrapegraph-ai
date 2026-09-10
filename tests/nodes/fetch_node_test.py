from langchain_core.documents import Document

from scrapegraphai.nodes import FetchNode


def test_fetch_html_convert_to_md_uses_source_as_baseurl(mocker):
    """convert_to_md must receive the fetched page's URL as baseurl, not the HTML itself."""
    content = "<html><body><a href='/relative'>link</a></body></html>"
    mock_loader_cls = mocker.patch("scrapegraphai.nodes.fetch_node.ChromiumLoader")
    mock_loader = mock_loader_cls.return_value
    mock_loader.load.return_value = [Document(page_content=content)]
    mock_convert = mocker.patch(
        "scrapegraphai.nodes.fetch_node.convert_to_md", return_value="converted"
    )

    node = FetchNode(
        input="url | local_dir",
        output=["doc_content"],
        node_config={"headless": False, "force": True},
    )
    source = "https://scrapegraph-ai.com/example"
    result = node.execute({"url": source})

    mock_convert.assert_called_once_with(content, source)
    assert result["doc_content"][0].page_content == "converted"


def test_fetch_html_use_soup_with_default_cut_does_not_raise(mocker):
    """use_soup with the default cut=True must not raise UnboundLocalError and
    must call convert_to_md with (html, source), not (source, html)."""
    html = "<html><body><a href='/relative'>link</a></body></html>"
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.text = html
    mocker.patch(
        "scrapegraphai.nodes.fetch_node.requests.get", return_value=mock_response
    )
    mock_convert = mocker.patch(
        "scrapegraphai.nodes.fetch_node.convert_to_md", return_value="converted"
    )

    node = FetchNode(
        input="url | local_dir",
        output=["doc_content"],
        node_config={"use_soup": True, "force": True},
    )
    source = "https://scrapegraph-ai.com/example"
    result = node.execute({"url": source})

    mock_convert.assert_called_once_with(html, source)
    assert result["doc_content"][0].page_content == "converted"


def test_fetch_html(mocker):
    title = "ScrapeGraph AI"
    link_url = "https://github.com/VinciGit00/Scrapegraph-ai"
    img_url = "https://raw.githubusercontent.com/VinciGit00/Scrapegraph-ai/main/docs/assets/scrapegraphai_logo.png"
    content = f"""
    <html>
      <head>
        <title>{title}</title>
      </head>
      <body>
        <a href="{link_url}">ScrapeGraphAI: You Only Scrape Once</a>
        <img src="{img_url}" alt="Scrapegraph-ai Logo">
      </body>
    </html>
    """
    mock_loader_cls = mocker.patch("scrapegraphai.nodes.fetch_node.ChromiumLoader")
    mock_loader = mock_loader_cls.return_value
    mock_loader.load.return_value = [Document(page_content=content)]
    node = FetchNode(
        input="url | local_dir",
        output=["doc", "links", "images"],
        node_config={"headless": False},
    )
    result = node.execute({"url": "https://scrapegraph-ai.com/example"})

    mock_loader.load.assert_called_once()
    doc = result["doc"][0]
    assert result is not None
    assert "ScrapeGraph AI" in doc.page_content
    assert "https://github.com/VinciGit00/Scrapegraph-ai" in doc.page_content
    assert (
        "https://raw.githubusercontent.com/VinciGit00/Scrapegraph-ai/main/docs/assets/scrapegraphai_logo.png"
        in doc.page_content
    )


def test_fetch_json():
    node = FetchNode(
        input="json",
        output=["doc"],
    )
    result = node.execute({"json": "inputs/example.json"})
    assert result is not None


def test_fetch_xml():
    node = FetchNode(
        input="xml",
        output=["doc"],
    )
    result = node.execute({"xml": "inputs/books.xml"})
    assert result is not None


def test_fetch_csv():
    node = FetchNode(
        input="csv",
        output=["doc"],
    )
    result = node.execute({"csv": "inputs/username.csv"})
    assert result is not None


def test_fetch_txt():
    node = FetchNode(
        input="txt",
        output=["doc", "links", "images"],
    )
    with open("inputs/plain_html_example.txt") as f:
        result = node.execute({"txt": f.read()})
    assert result is not None
