from langchain_core.documents import Document

from scrapegraphai.nodes import SearchLinkNode


def _filtered_links(links, url="https://example.com"):
    node = SearchLinkNode(
        input="doc",
        output=["parsed_doc"],
        node_config={"filter_links": True},
    )
    state = {"doc": [Document(page_content=" ".join(links))], "url": url}
    return node.execute(state)["parsed_doc"]


def test_language_filter_keeps_paths_that_only_start_with_a_language_code():
    links = [
        "https://example.com/details/42",
        "https://example.com/items/7",
        "https://example.com/free-trial",
        "https://example.com/developers",
        "https://example.com/esports",
    ]

    assert sorted(_filtered_links(links)) == sorted(links)


def test_language_filter_drops_language_paths_and_lang_query():
    links = [
        "https://example.com/fr",
        "https://example.com/fr/produits",
        "https://example.com/pt-br/produtos",
        "https://example.com/de_de/produkte",
        "https://example.com/products?lang=es",
    ]

    assert _filtered_links(links) == []
