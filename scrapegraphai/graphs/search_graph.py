"""
Module for creating the search graph
"""
from ..models import OpenAI, Gemini
from .base_graph import BaseGraph
from ..nodes import (
    FetchNode,
    ParseNode,
    RAGNode,
    GenerateAnswerNode
)
from ..nodes.search_internet_node import SearchInternetNode


class SearchGraph:
    """ 
    Module for searching info on the internet
    """

    def __init__(self, prompt: str, file_source: str, config: dict):
        """
        Initializes SmartScraper with a prompt, URL, and language model configuration.
        """
        self.prompt = prompt
        self.file_source = file_source
        self.input_key = "url" if file_source.startswith(
            "http") else "local_dir"
        self.config = config
        self.llm_model = self._create_llm(config["llm"])
        self.graph = self._create_graph()

    def _create_llm(self, llm_config: dict):
        """
        Creates an instance of the ChatOpenAI class with the provided language model configuration.

        Returns:
            ChatOpenAI: An instance of the ChatOpenAI class.

        Raises:
            ValueError: If 'api_key' is not provided in llm_config.
        """
        llm_defaults = {
            "temperature": 0,
            "streaming": True
        }
        # Update defaults with any LLM parameters that were provided
        llm_params = {**llm_defaults, **llm_config}
        # Ensure the api_key is set, raise an error if it's not
        if "api_key" not in llm_params:
            raise ValueError("LLM configuration must include an 'api_key'.")
        # select the model based on the model name
        if "gpt-" in llm_params["model"]:
            return OpenAI(llm_params)
        elif "gemini" in llm_params["model"]:
            return Gemini(llm_params)
        else:
            raise ValueError("Model not supported")

    def _create_graph(self):
        """
        Creates the graph of nodes representing the workflow for web scraping.

        Returns:
            BaseGraph: An instance of the BaseGraph class.
        """
        # define the nodes for the graph
        search_internet_node = SearchInternetNode(
            input="url | local_dir",
            output=["doc"],
            model_config={"llm_model": self.llm_model},
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
