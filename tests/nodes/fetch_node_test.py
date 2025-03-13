from langchain_core.documents import Document

from scrapegraphai.nodes import FetchNode


def test_fetch_html(monkeypatch):
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
    # Define a fake ChromiumLoader that returns our fixed content
    class FakeChromiumLoader:
        def __init__(self, sources, headless, storage_state, **loader_kwargs):
            self.sources = sources
            self.headless = headless
            self.storage_state = storage_state
            self.loader_kwargs = loader_kwargs

        def load(self):
            return [Document(page_content=content)]

    # Use monkeypatch to replace ChromiumLoader with FakeChromiumLoader
    monkeypatch.setattr("scrapegraphai.nodes.fetch_node.ChromiumLoader", FakeChromiumLoader)
    node = FetchNode(
        input="url | local_dir",
        output=["doc", "links", "images"],
        node_config={"headless": False},
    )
    result = node.execute({"url": "https://scrapegraph-ai.com/example"})

    doc = result["doc"][0]
    assert result is not None
    assert "ScrapeGraph AI" in doc.page_content
    assert "https://github.com/VinciGit00/Scrapegraph-ai" in doc.page_content
    assert (
        "https://raw.githubusercontent.com/VinciGit00/Scrapegraph-ai/main/docs/assets/scrapegraphai_logo.png"
        in doc.page_content
    )


def test_fetch_json():
    """Test fetching content from a JSON file by creating a dummy JSON file"""
    import os
    os.makedirs("inputs", exist_ok=True)
    with open("inputs/example.json", "w", encoding="utf-8") as f:
        f.write('{"test": "json content"}')
    node = FetchNode(
        input="json",
        output=["doc"],
    )
    result = node.execute({"json": "inputs/example.json"})
    assert result is not None


def test_fetch_xml():
    """Test fetching content from an XML file by creating a dummy XML file"""
    import os
    os.makedirs("inputs", exist_ok=True)
    with open("inputs/books.xml", "w", encoding="utf-8") as f:
        f.write("<books><book>Test Book</book></books>")
    node = FetchNode(
        input="xml",
        output=["doc"],
    )
    result = node.execute({"xml": "inputs/books.xml"})
    assert result is not None


def test_fetch_csv():
    """Test fetching content from a CSV file by creating a dummy CSV file and mocking pandas if necessary"""
    import os
    os.makedirs("inputs", exist_ok=True)
    with open("inputs/username.csv", "w", encoding="utf-8") as f:
        f.write("col1,col2\nvalue1,value2")
    import sys, types
    if "pandas" not in sys.modules:
        dummy_pandas = types.ModuleType("pandas")
        dummy_pandas.read_csv = lambda path: {"col1": ["value1"], "col2": ["value2"]}
        sys.modules["pandas"] = dummy_pandas
    node = FetchNode(
        input="csv",
        output=["doc"],
    )
    result = node.execute({"csv": "inputs/username.csv"})
    assert result is not None


def test_fetch_txt():
    """Test fetching content from a plain text file by creating a dummy text file with HTML content"""
    import os
    os.makedirs("inputs", exist_ok=True)
    with open("inputs/plain_html_example.txt", "w", encoding="utf-8") as f:
        f.write("<html><body>Test plain HTML content</body></html>")
    node = FetchNode(
        input="local_dir",
        output=["doc", "links", "images"],
    )
    with open("inputs/plain_html_example.txt") as f:
        result = node.execute({"local_dir": f.read()})
    assert result is not None
