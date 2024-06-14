from scrapegraphai.nodes import FetchNode
from langchain_core.documents import Document


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
    assert title in doc.page_content
    assert link_url in result["links"]
    assert img_url in result["images"]


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
