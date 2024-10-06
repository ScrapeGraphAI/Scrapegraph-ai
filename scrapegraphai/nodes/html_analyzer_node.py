"""
HtmlAnalyzerNode Module
"""
from typing import List, Optional
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_models import ChatOllama
from .base_node import BaseNode
from ..utils import reduce_html
from ..prompts import (
    TEMPLATE_HTML_ANALYSIS, TEMPLATE_HTML_ANALYSIS_WITH_CONTEXT
)

class HtmlAnalyzerNode(BaseNode):
    """
    A node that generates an analysis of the provided HTML code based on the wanted infromations to be extracted.
    
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
        node_name: str = "HtmlAnalyzer",
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

    def execute(self, state: dict) -> dict:
        """
        Generates an analysis of the provided HTML code based on the wanted infromations to be extracted.

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
        refined_prompt = input_data[0]
        html = input_data[1]
        reduced_html = reduce_html(html[0].page_content, self.node_config.get("reduction", 0))

        if self.additional_info is not None:
            prompt = PromptTemplate(
                template=TEMPLATE_HTML_ANALYSIS_WITH_CONTEXT,
                partial_variables={"initial_analysis": refined_prompt,
                                    "html_code": reduced_html,
                                    "additional_context": self.additional_info})
        else:
            prompt = PromptTemplate(
                template=TEMPLATE_HTML_ANALYSIS,
                partial_variables={"initial_analysis": refined_prompt,
                                    "html_code": reduced_html})

        output_parser = StrOutputParser()

        chain =  prompt | self.llm_model | output_parser
        html_analysis = chain.invoke({})

        state.update({self.output[0]: html_analysis, self.output[1]: reduced_html})
        return state
