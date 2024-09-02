"""
SearchInternetNode Module
"""
from typing import List, Optional
from langchain.output_parsers import CommaSeparatedListOutputParser
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOllama
from ..utils.logging import get_logger
from ..utils.research_web import search_on_web
from .base_node import BaseNode
from ..prompts import TEMPLATE_SEARCH_INTERNET

class SearchInternetNode(BaseNode):
    """
    A node that generates a search query based on the user's input and searches the internet
    for relevant information. The node constructs a prompt for the language model, submits it,
    and processes the output to generate a search query. It then uses the search query to find
    relevant information on the internet and updates the state with the generated answer.

    Attributes:
        llm_model: An instance of the language model client used for generating search queries.
        verbose (bool): A flag indicating whether to show print statements during execution.

    Args:
        input (str): Boolean expression defining the input keys needed from the state.
        output (List[str]): List of output keys to be updated in the state.
        node_config (dict): Additional configuration for the node.
        node_name (str): The unique identifier name for the node, defaulting to "SearchInternet".
    """

    def __init__(
        self,
        input: str,
        output: List[str],
        node_config: Optional[dict] = None,
        node_name: str = "SearchInternet",
    ):
        super().__init__(node_name, "node", input, output, 1, node_config)

        self.llm_model = node_config["llm_model"]
        self.verbose = (
            False if node_config is None else node_config.get("verbose", False)
        )
        self.search_engine = (
            node_config["search_engine"]
            if node_config.get("search_engine")
            else "google"
        )
        self.max_results = node_config.get("max_results", 3)

    def execute(self, state: dict) -> dict:
        """
        Generates an answer by constructing a prompt from the user's input and the scraped
        content, querying the language model, and parsing its response.

        The method updates the state with the generated answer.

        Args:
            state (dict): The current state of the graph. The input keys will be used to fetch the
                            correct data types from the state.

        Returns:
            dict: The updated state with the output key containing the generated answer.

        Raises:
            KeyError: If the input keys are not found in the state, indicating that the
                        necessary information for generating the answer is missing.
        """

        self.logger.info(f"--- Executing {self.node_name} Node ---")

        input_keys = self.get_input_keys(state)

        input_data = [state[key] for key in input_keys]

        user_prompt = input_data[0]

        output_parser = CommaSeparatedListOutputParser()

        search_prompt = PromptTemplate(
            template=TEMPLATE_SEARCH_INTERNET,
            input_variables=["user_prompt"],
        )

        search_answer = search_prompt | self.llm_model | output_parser

        if isinstance(self.llm_model, ChatOllama) and self.llm_model.format == 'json':
            self.llm_model.format = None
            search_query = search_answer.invoke({"user_prompt": user_prompt})[0]
            self.llm_model.format = 'json'
        else:
            search_query = search_answer.invoke({"user_prompt": user_prompt})[0]

        self.logger.info(f"Search Query: {search_query}")

        answer = search_on_web(query=search_query, max_results=self.max_results,
                               search_engine=self.search_engine)

        if len(answer) == 0:
            raise ValueError("Zero results found for the search query.")

        state.update({self.output[0]: answer})
        return state
