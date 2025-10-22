"""
SearchInternetNode Module
"""

from typing import List, Optional

from langchain_core.output_parsers import CommaSeparatedListOutputParser
from langchain_core.prompts import PromptTemplate
from tqdm import tqdm

from ..prompts import (
    TEMPLATE_SEARCH_WITH_CONTEXT_CHUNKS,
    TEMPLATE_SEARCH_WITH_CONTEXT_NO_CHUNKS,
)
from .base_node import BaseNode


class SearchLinksWithContext(BaseNode):
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
        node_name (str): The unique identifier name for the node,
        defaulting to "SearchLinksWithContext".
    """

    def __init__(
        self,
        input: str,
        output: List[str],
        node_config: Optional[dict] = None,
        node_name: str = "SearchLinksWithContext",
    ):
        super().__init__(node_name, "node", input, output, 2, node_config)
        self.llm_model = node_config["llm_model"]
        self.verbose = (
            True if node_config is None else node_config.get("verbose", False)
        )

    def execute(self, state: dict) -> dict:
        """
        Generates an answer by constructing a prompt from the user's input and the scraped
        content, querying the language model, and parsing its response.

        Args:
            state (dict): The current state of the graph. The input keys will be used
                            to fetch the correct data from the state.

        Returns:
            dict: The updated state with the output key containing the generated answer.

        Raises:
            KeyError: If the input keys are not found in the state, indicating
                      that the necessary information for generating an answer is missing.
        """

        self.logger.info(f"--- Executing {self.node_name} Node ---")

        input_keys = self.get_input_keys(state)

        input_data = [state[key] for key in input_keys]

        doc = input_data[1]

        output_parser = CommaSeparatedListOutputParser()
        format_instructions = output_parser.get_format_instructions()

        result = []

        for i, chunk in enumerate(
            tqdm(doc, desc="Processing chunks", disable=not self.verbose)
        ):
            if len(doc) == 1:
                prompt = PromptTemplate(
                    template=TEMPLATE_SEARCH_WITH_CONTEXT_CHUNKS,
                    input_variables=["question"],
                    partial_variables={
                        "context": chunk.page_content,
                        "format_instructions": format_instructions,
                    },
                )
            else:
                prompt = PromptTemplate(
                    template=TEMPLATE_SEARCH_WITH_CONTEXT_NO_CHUNKS,
                    input_variables=["question"],
                    partial_variables={
                        "context": chunk.page_content,
                        "chunk_id": i + 1,
                        "format_instructions": format_instructions,
                    },
                )

            result.extend(prompt | self.llm_model | output_parser)

        state["urls"] = result
        return state
