"""
PromptRefinerNode Module
"""
from typing import List, Optional
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_models import ChatOllama
from .base_node import BaseNode
from ..utils import transform_schema
from ..prompts import (
    TEMPLATE_REFINER, TEMPLATE_REFINER_WITH_CONTEXT
)

class PromptRefinerNode(BaseNode):
    """
    A node that refine the user prompt with the use of the schema and additional context and
    create a precise prompt in subsequent steps that explicitly link elements in the user's 
    original input to their corresponding representations in the JSON schema.

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
        node_name: str = "PromptRefiner",
    ):
        super().__init__(node_name, "node", input, output, 2, node_config)

        self.llm_model = node_config["llm_model"]

        if isinstance(node_config["llm_model"], ChatOllama):
            self.llm_model.format="json"

        self.verbose = (
            True if node_config is None else node_config.get("verbose", False)
        )
        self.force = (
            False if node_config is None else node_config.get("force", False)
        )
        self.script_creator = (
            False if node_config is None else node_config.get("script_creator", False)
        )
        self.is_md_scraper = (
            False if node_config is None else node_config.get("is_md_scraper", False)
        )

        self.additional_info = node_config.get("additional_info")

        self.output_schema = node_config.get("schema")

    def execute(self, state: dict) -> dict:
        """
        Generate a refined prompt using the user's prompt, the schema, and additional context.

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

        user_prompt = state['user_prompt']

        self.simplefied_schema = transform_schema(self.output_schema.schema())

        if self.additional_info is not None:
            prompt = PromptTemplate(
                template=TEMPLATE_REFINER_WITH_CONTEXT,
                partial_variables={"user_input": user_prompt,
                                    "json_schema": str(self.simplefied_schema),
                                    "additional_context": self.additional_info})
        else:
            prompt = PromptTemplate(
                template=TEMPLATE_REFINER,
                partial_variables={"user_input": user_prompt,
                                    "json_schema": str(self.simplefied_schema)})

        output_parser = StrOutputParser()

        chain =  prompt | self.llm_model | output_parser
        refined_prompt = chain.invoke({})

        state.update({self.output[0]: refined_prompt})
        return state
