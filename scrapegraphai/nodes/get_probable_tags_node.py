"""
GetProbableTagsNode Module
"""

from typing import List

from langchain_core.output_parsers import CommaSeparatedListOutputParser
from langchain_core.prompts import PromptTemplate

from ..prompts import TEMPLATE_GET_PROBABLE_TAGS
from .base_node import BaseNode


class GetProbableTagsNode(BaseNode):
    """
    A node that utilizes a language model to identify probable HTML tags within a document that
    are likely to contain the information relevant to a user's query. This node generates a prompt
    describing the task, submits it to the language model, and processes the output to produce a
    list of probable tags.

    Attributes:
        llm_model: An instance of the language model client used for tag predictions.

    Args:
        input (str): Boolean expression defining the input keys needed from the state.
        output (List[str]): List of output keys to be updated in the state.
        model_config (dict): Additional configuration for the language model.
        node_name (str): The unique identifier name for the node, defaulting to "GetProbableTags".
    """

    def __init__(
        self,
        input: str,
        output: List[str],
        node_config: dict,
        node_name: str = "GetProbableTags",
    ):
        super().__init__(node_name, "node", input, output, 2, node_config)

        self.llm_model = node_config["llm_model"]
        self.verbose = (
            False if node_config is None else node_config.get("verbose", False)
        )

    def execute(self, state: dict) -> dict:
        """
        Generates a list of probable HTML tags based on the user's input and updates the state
        with this list. The method constructs a prompt for the language model, submits it, and
        parses the output to identify probable tags.

        Args:
            state (dict): The current state of the graph. The input keys will be used to fetch the
                            correct data types from the state.

        Returns:
            dict: The updated state with the input key containing a list of probable HTML tags.

        Raises:
            KeyError: If input keys are not found in the state, indicating that the
                      necessary information for generating tag predictions is missing.
        """

        self.logger.info(f"--- Executing {self.node_name} Node ---")

        input_keys = self.get_input_keys(state)

        input_data = [state[key] for key in input_keys]

        user_prompt = input_data[0]
        url = input_data[1]

        output_parser = CommaSeparatedListOutputParser()
        format_instructions = output_parser.get_format_instructions()

        template = TEMPLATE_GET_PROBABLE_TAGS

        tag_prompt = PromptTemplate(
            template=template,
            input_variables=["question"],
            partial_variables={
                "format_instructions": format_instructions,
                "webpage": url,
            },
        )

        tag_answer = tag_prompt | self.llm_model | output_parser
        probable_tags = tag_answer.invoke({"question": user_prompt})

        state.update({self.output[0]: probable_tags})
        return state
