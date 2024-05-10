"""
SmartScraperGraph Module Burr Version
"""

from typing import Tuple

from burr import tracking
from burr.core import Application, ApplicationBuilder, State, default, when
from burr.core.action import action

from langchain_community.document_loaders import AsyncChromiumLoader
from langchain_core.documents import Document
if __name__ == '__main__':
    from scrapegraphai.utils.remover import remover
else:
    from ..utils.remover import remover


def fetch_node(source: str,
               headless: bool = True
               ) -> Document:
    if not source.startswith("http"):
        return Document(page_content=remover(source), metadata={
            "source": "local_dir"
        })
    else:
        loader = AsyncChromiumLoader(
            [source],
            headless=headless,
        )
        document = loader.load()
        return Document(page_content=remover(str(document[0].page_content)))

def parse_node(fetch_node: Document, chunk_size: int) -> list[Document]:

    pass

def rag_node(parse_node: list[Document], llm_model: object, embedder_model: object) -> list[Document]:
    pass

def generate_answer_node(rag_node: list[Document], llm_model: object) -> str:
    pass


if __name__ == '__main__':
    from hamilton import driver
    import __main__ as smart_scraper_graph_hamilton
    dr = (
        driver.Builder()
        .with_modules(smart_scraper_graph_hamilton)
        .with_config({})
        .build()
    )
    dr.display_all_functions("smart_scraper.png")

    # config = {
    #     "llm_model": "rag-token",
    #     "embedder_model": "foo",
    #     "model_token": "bar",
    # }
    #
    # result = dr.execute(
    #     ["generate_answer_node"],
    #     inputs={
    #         "prompt": "What is the capital of France?",
    #         "source": "https://en.wikipedia.org/wiki/Paris",
    #     }
    # )
    #
    # print(result)