"""
MarkdownifyNode Module
"""

from typing import List, Optional

from ..utils.convert_to_md import convert_to_md
from .base_node import BaseNode


class MarkdownifyNode(BaseNode):
    """
    A node responsible for converting HTML content to Markdown format.

    This node takes HTML content from the state and converts it to clean, readable Markdown.
    It uses the convert_to_md utility function to perform the conversion.

    Attributes:
        verbose (bool): A flag indicating whether to show print statements during execution.

    Args:
        input (str): Boolean expression defining the input keys needed from the state.
        output (List[str]): List of output keys to be updated in the state.
        node_config (Optional[dict]): Additional configuration for the node.
        node_name (str): The unique identifier name for the node, defaulting to "Markdownify".
    """

    def __init__(
        self,
        input: str,
        output: List[str],
        node_config: Optional[dict] = None,
        node_name: str = "Markdownify",
    ):
        super().__init__(node_name, "node", input, output, 1, node_config)

        self.verbose = (
            False if node_config is None else node_config.get("verbose", False)
        )

    def execute(self, state: dict) -> dict:
        """
        Executes the node's logic to convert HTML content to Markdown.

        Args:
            state (dict): The current state of the graph. The input keys will be used to fetch the
                         HTML content from the state.

        Returns:
            dict: The updated state with the output key containing the Markdown content.

        Raises:
            KeyError: If the input keys are not found in the state, indicating that the
                     necessary HTML content is missing.
        """
        self.logger.info(f"--- Executing {self.node_name} Node ---")

        input_keys = self.get_input_keys(state)
        html_content = state[input_keys[0]]

        # Convert HTML to Markdown
        markdown_content = convert_to_md(html_content)

        # Update state with markdown content
        state.update({self.output[0]: markdown_content})

        return state
