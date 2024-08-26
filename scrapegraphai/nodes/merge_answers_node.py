"""
MergeAnswersNode Module
"""
from typing import List, Optional
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from ..utils.logging import get_logger
from .base_node import BaseNode
from ..prompts import TEMPLATE_COMBINED

class MergeAnswersNode(BaseNode):
    """
    A node responsible for merging the answers from multiple graph instances into a single answer.

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

        input_keys = self.get_input_keys(state)

        input_data = [state[key] for key in input_keys]

        user_prompt = input_data[0]
        answers = input_data[1]

        answers_str = ""
        for i, answer in enumerate(answers):
            answers_str += f"CONTENT WEBSITE {i+1}: {answer}\n"

        if self.node_config.get("schema", None) is not None:
            output_parser = JsonOutputParser(pydantic_object=self.node_config["schema"])
        else:
            output_parser = JsonOutputParser()

        format_instructions = output_parser.get_format_instructions()

        prompt_template = PromptTemplate(
            template=TEMPLATE_COMBINED,
            input_variables=["user_prompt"],
            partial_variables={
                "format_instructions": format_instructions,
                "website_content": answers_str,
            },
        )

        merge_chain = prompt_template | self.llm_model | output_parser
        answer = merge_chain.invoke({"user_prompt": user_prompt})

        state.update({self.output[0]: answer})
        return state
