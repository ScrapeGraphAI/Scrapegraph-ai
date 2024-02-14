""" 
Module for creating the smart scaper
"""
from langchain_openai import ChatOpenAI
from .base_graph import BaseGraph
from ..nodes import FetchHTMLNode, ConditionalNode, GetProbableTagsNode
from ..nodes import GenerateAnswerNode, ParseHTMLNode


class SmartScraper:
    """
    SmartScraper is a comprehensive web scraping tool that automates the process of extracting
    information from web pages using a natural language model to interpret and answer prompts.

    Attributes:
        prompt (str): The user's natural language prompt for the information to be extracted.
        url (str): The URL of the web page to scrape.
        llm_config (dict): Configuration parameters for the language model, with 
        'api_key' being mandatory.
        llm (ChatOpenAI): An instance of the ChatOpenAI class configured with llm_config.
        graph (BaseGraph): An instance of the BaseGraph class representing the scraping workflow.

    Methods:
        run(): Executes the web scraping process and returns the answer to the prompt.

    Args:
        prompt (str): The user's natural language prompt for the information to be extracted.
        url (str): The URL of the web page to scrape.
        llm_config (dict): A dictionary containing configuration options for the language model.
                           Must include 'api_key', may also specify 'model_name', 
                           'temperature', and 'streaming'.
    """

    def __init__(self, prompt: str, url: str, llm_config: dict):
        """
        Initializes the SmartScraper with a prompt, URL, and language model configuration.
        """
        self.prompt = prompt
        self.url = url
        self.llm_config = llm_config
        self.llm = self._create_llm()
        self.graph = self._create_graph()

    def _create_llm(self):
        """
        Creates an instance of the ChatOpenAI class with the provided language model configuration.

        Returns:
            ChatOpenAI: An instance of the ChatOpenAI class.

        Raises:
            ValueError: If 'api_key' is not provided in llm_config.
        """
        llm_defaults = {
            "model_name": "gpt-3.5-turbo",
            "temperature": 0,
            "streaming": True
        }
        # Update defaults with any LLM parameters that were provided
        llm_params = {**llm_defaults, **self.llm_config}
        # Ensure the api_key is set, raise an error if it's not
        if "api_key" not in llm_params:
            raise ValueError("LLM configuration must include an 'api_key'.")
        # Create the ChatOpenAI instance with the provided and default parameters
        return ChatOpenAI(**llm_params)

    def _create_graph(self):
        """
        Creates the graph of nodes representing the workflow for web scraping.

        Returns:
            BaseGraph: An instance of the BaseGraph class.
        """
        fetch_html_node = FetchHTMLNode("fetch_html")
        get_probable_tags_node = GetProbableTagsNode(
            self.llm, "get_probable_tags")
        parse_document_node = ParseHTMLNode("parse_document")
        generate_answer_node = GenerateAnswerNode(self.llm, "generate_answer")
        conditional_node = ConditionalNode(
            "conditional", [parse_document_node, generate_answer_node])

        return BaseGraph(
            nodes={
                fetch_html_node,
                get_probable_tags_node,
                conditional_node,
                parse_document_node,
                generate_answer_node,
            },
            edges={
                (fetch_html_node, get_probable_tags_node),
                (get_probable_tags_node, conditional_node),
                (parse_document_node, generate_answer_node)
            },
            entry_point=fetch_html_node
        )

    def run(self) -> str:
        """
        Executes the scraping process by running the graph and returns the extracted information.

        Returns:
            str: The answer extracted from the web page, corresponding to the given prompt.
        """
        inputs = {"keys": {"user_input": self.prompt, "url": self.url}}
        final_state = self.graph.execute(inputs)
        return final_state["keys"].get("answer", "No answer found.")
