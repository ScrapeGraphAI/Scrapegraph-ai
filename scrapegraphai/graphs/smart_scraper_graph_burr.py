"""
SmartScraperGraph Module Burr Version
"""
from typing import Tuple

from burr import tracking
from burr.core import Application, ApplicationBuilder, State, default, when
from burr.core.action import action

from langchain_community.document_loaders import AsyncChromiumLoader
from langchain_core.documents import Document
from ..utils.remover import remover


@action(reads=["url", "local_dir"], writes=["doc"])
def fetch_node(state: State, headless: bool = True, verbose: bool = False) -> tuple[dict, State]:
    if verbose:
        print(f"--- Executing Fetch Node ---")

    source = state.get("url", state.get("local_dir"))

    if self.input == "json_dir" or self.input == "xml_dir" or self.input == "csv_dir":
        compressed_document = [Document(page_content=source, metadata={
            "source": "local_dir"
        })]
    # if it is a local directory
    elif not source.startswith("http"):
        compressed_document = [Document(page_content=remover(source), metadata={
            "source": "local_dir"
        })]

    else:
        if self.node_config is not None and self.node_config.get("endpoint") is not None:

            loader = AsyncChromiumLoader(
                [source],
                proxies={"http": self.node_config["endpoint"]},
                headless=headless,
            )
        else:
            loader = AsyncChromiumLoader(
                [source],
                headless=headless,
            )

        document = loader.load()
        compressed_document = [
            Document(page_content=remover(str(document[0].page_content)))]

    return {"doc": compressed_document}, state.update(doc=compressed_document)

@action(reads=["doc"], writes=["parsed_doc"])
def parse_node(state: State, chunk_size: int) -> tuple[dict, State]:
    return {}, state

@action(reads=["user_prompt", "parsed_doc", "doc"],
        writes=["relevant_chunks"])
def rag_node(state: State, llm_model: object, embedder_model: object) -> tuple[dict, State]:
    return {}, state

@action(reads=["user_prompt", "relevant_chunks", "parsed_doc", "doc"],
        writes=["answer"])
def generate_answer_node(state: State, llm_model: object) -> tuple[dict, State]:
    return {}, state

def run(prompt: str, input_key: str, source: str, config: dict) -> str:

    llm_model = config["llm_model"]
    embedder_model = config["embedder_model"]
    chunk_size = config["model_token"]

    initial_state = {
        "user_prompt": prompt,
        input_key: source
    }
    app = (
        ApplicationBuilder()
        .with_actions(
            fetch_node=fetch_node,
            parse_node=parse_node,
            rag_node=rag_node,
            generate_answer_node=generate_answer_node
        )
        .with_transitions(
            ("fetch_node", "parse_node", default),
            ("parse_node", "rag_node", default),
            ("rag_node", "generate_answer_node", default)
        )
        .with_entrypoint("fetch_node")
        .with_state(**initial_state)
        .build()
    )
    app.visualize(
        output_file_path="smart_scraper_graph",
        include_conditions=False, view=True, format="png"
    )
    # last_action, result, state = app.run(
    #     halt_after=["generate_answer_node"],
    #     inputs={
    #         "llm_model": llm_model,
    #         "embedder_model": embedder_model,
    #         "model_token": chunk_size
    #     }
    # )
    # return result.get("answer", "No answer found.")

if __name__ == '__main__':

    prompt = "What is the capital of France?"
    source = "https://en.wikipedia.org/wiki/Paris"
    input_key = "url"
    config = {
        "llm_model": "rag-token",
        "embedder_model": "foo",
        "model_token": "bar",
    }
    run(prompt, input_key, source, config)