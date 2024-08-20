from scrapegraphai.graphs import SearchLinkGraph
from scrapegraphai.utils import prettify_exec_info

def test_smart_scraper_pipeline():
    graph_config = {
        "llm": {
            "model": "ollama/llama3.1",
            "temperature": 0,
            "format": "json",
        },
        "verbose": True,
        "headless": False
    }

    smart_scraper_graph = SearchLinkGraph(
        source="https://sport.sky.it/nba?gr=www",
        config=graph_config
    )

    result = smart_scraper_graph.run()

    assert result is not None
