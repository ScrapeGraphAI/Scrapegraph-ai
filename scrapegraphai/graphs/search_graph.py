""" 
Module for making the search on the intenet
"""
from ..models import OpenAI, Gemini
from .base_graph import BaseGraph
from ..nodes import (
    SearchInternetNode,
    FetchNode,
    ParseNode,
    RAGNode,
    GenerateAnswerNode
)
from .abstract_graph import AbstractGraph


class SearchGraph(AbstractGraph):
    """ 
    Module for searching info on the internet
    """

    def _create_llm(self, llm_config: dict):
        """
        Creates an instance of the language model (OpenAI or Gemini) based on configuration.
        """
        llm_defaults = {
            "temperature": 0,
            "streaming": True
        }
        llm_params = {**llm_defaults, **llm_config}
        if "api_key" not in llm_params:
            raise ValueError("LLM configuration must include an 'api_key'.")
        if "gpt-" in llm_params["model"]:
            return OpenAI(llm_params)
        elif "gemini" in llm_params["model"]:
            return Gemini(llm_params)
        else:
            raise ValueError("Model not supported")

    def _create_graph(self):
        """
        Creates the graph of nodes representing the workflow for web scraping and searching.
        """
        search_internet_node = SearchInternetNode(
            input="user_prompt",
            output=["url"],
            model_config={"llm_model": self.llm_model}
        )
        fetch_node = FetchNode(
            input="url | local_dir",
            output=["doc"],
        )
        parse_node = ParseNode(
            input="doc",
            output=["parsed_doc"],
        )
        rag_node = RAGNode(
            input="user_prompt & (parsed_doc | doc)",
            output=["relevant_chunks"],
            model_config={"llm_model": self.llm_model},
        )
        generate_answer_node = GenerateAnswerNode(
            input="user_prompt & (relevant_chunks | parsed_doc | doc)",
            output=["answer"],
            model_config={"llm_model": self.llm_model},
        )

        return BaseGraph(
            nodes={
                search_internet_node,
                fetch_node,
                parse_node,
                rag_node,
                generate_answer_node,
            },
            edges={
                (search_internet_node, fetch_node),
                (fetch_node, parse_node),
                (parse_node, rag_node),
                (rag_node, generate_answer_node)
            },
            entry_point=search_internet_node
        )

    def run(self) -> str:
        """
        Executes the web scraping and searching process.
        """
        inputs = {"user_prompt": self.prompt}
        final_state = self.graph.execute(inputs)

        return final_state.get("answer", "No answer found.")
