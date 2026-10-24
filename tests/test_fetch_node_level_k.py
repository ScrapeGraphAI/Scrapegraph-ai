from unittest.mock import patch

from langchain_core.documents import Document

from scrapegraphai.nodes.fetch_node_level_k import FetchNodeLevelK


def test_empty_page_does_not_skip_the_next_link():
    """A page with empty content must not stop the following page from loading."""
    pages = {
        "https://example.com": '<a href="/empty">E</a><a href="/full">F</a>',
        "https://example.com/empty": "   ",
        "https://example.com/full": "<p>content</p>",
    }

    def fake_fetch(source, loader_kwargs):
        return [Document(page_content=pages[source])]

    node = FetchNodeLevelK(
        input="url",
        output=["docs"],
        node_config={"depth": 2},
    )

    with patch.object(node, "fetch_content", side_effect=fake_fetch) as fetch:
        state = node.execute({"url": "https://example.com"})

    fetched = [call.args[0] for call in fetch.call_args_list]
    assert "https://example.com/full" in fetched
    assert [doc["source"] for doc in state["docs"]] == [
        "https://example.com",
        "https://example.com/full",
    ]
