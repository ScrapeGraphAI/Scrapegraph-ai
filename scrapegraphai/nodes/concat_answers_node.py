"""
ConcatAnswersNode Module
"""
from typing import List, Optional
from ..utils.logging import get_logger
from .base_node import BaseNode

class ConcatAnswersNode(BaseNode):
    """
    A node responsible for concatenating the answers from multiple 
    graph instances into a single answer.

    Attributes:
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
        node_name: str = "ConcatAnswers",
    ):
        super().__init__(node_name, "node", input, output, 1, node_config)

        self.verbose = (
            False if node_config is None else node_config.get("verbose", False)
        )

    def _merge_dict(self, items):

        return {"products": {f"item_{i+1}": item for i, item in enumerate(items)}}

    def execute(self, state: dict) -> dict:
        """
        Executes the node's logic to concatenate the answers from multiple graph instances into a
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

        input_keys = self.get_input_keys(state)

        input_data = [state[key] for key in input_keys]

        answers = input_data[0]

        if len(answers) > 1:
            answer = self._merge_dict(answers)

            state.update({self.output[0]: answer})

        else:
            state.update({self.output[0]: answers[0]})
        return state
