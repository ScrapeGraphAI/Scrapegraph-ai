"""
MergeAnswersNode Module
"""

# Imports from standard library
from typing import List, Optional
from tqdm import tqdm

# Imports from Langchain
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from tqdm import tqdm

from ..utils.logging import get_logger

# Imports from the library
from .base_node import BaseNode


class MergeGeneratedScriptsNode(BaseNode):
    """
    A node responsible for merging scripts generated.
    Attributes:
        llm_model: An instance of a language model client, configured for generating answers.
        verbose (bool): A flag indicating whether to show print statements during execution.
    Args:
        input (str): Boolean expression defining the input keys needed from the state.
        output (List[str]): List of output keys to be updated in the state.
        node_config (dict): Additional configuration for the node.
        node_name (str): The unique identifier name for the node, defaulting to "GenerateAnswer".
    """

    def __init__(
        self,
        input: str,
        output: List[str],
        node_config: Optional[dict] = None,
        node_name: str = "MergeAnswers",
    ):
        super().__init__(node_name, "node", input, output, 2, node_config)

        self.llm_model = node_config["llm_model"]
        self.verbose = (
            False if node_config is None else node_config.get("verbose", False)
        )

    def execute(self, state: dict) -> dict:
        """
        Executes the node's logic to merge the answers from multiple graph instances into a
        single answer.
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

        # Interpret input keys based on the provided input expression
        input_keys = self.get_input_keys(state)

        # Fetching data from the state based on the input keys
        input_data = [state[key] for key in input_keys]

        scripts = input_data[1]

        # merge the answers in one string
        for i, script_str in enumerate(scripts):
            print(f"Script #{i}")
            print("=" * 40)
            print(script_str)
            print("-" * 40)

        # Update the state with the generated answer
        state.update({self.output[0]: scripts})
        return state