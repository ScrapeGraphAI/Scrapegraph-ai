"""
MergeAnswersNode Module
"""

# Imports from standard library
from typing import List, Optional
from tqdm import tqdm

# Imports from Langchain
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
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
        node_name: str = "MergeGeneratedScripts",
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

        user_prompt = input_data[0]
        scripts = input_data[1]

        # merge the scripts in one string
        scripts_str = ""
        for i, script in enumerate(scripts):
            scripts_str += "-----------------------------------\n"
            scripts_str += f"SCRIPT URL {i+1}\n"
            scripts_str += "-----------------------------------\n"
            scripts_str += script

        # TODO: should we pass the schema to the output parser even if the scripts already have it implemented?

        # schema to be used for output parsing
        # if self.node_config.get("schema", None) is not None:
        #     output_schema = JsonOutputParser(pydantic_object=self.node_config["schema"])
        # else:
        #     output_schema = JsonOutputParser()

        # format_instructions = output_schema.get_format_instructions()

        template_merge = """
        You are a python expert in web scraping and you have just generated multiple scripts to scrape different URLs.\n
        The scripts are generated based on a user question and the content of the websites.\n
        You need to create one single script that merges the scripts generated for each URL.\n
        The scraped contents are in a JSON format and you need to merge them based on the context and providing a correct JSON structure.\n
        The output should be just in python code without any comment and should implement the main function.\n
        The python script, when executed, should format the extracted information sticking to the user question and scripts output format.\n
        USER PROMPT: {user_prompt}\n
        SCRIPTS:\n
        {scripts}
        """

        prompt_template = PromptTemplate(
            template=template_merge,
            input_variables=["user_prompt"],
            partial_variables={
                "scripts": scripts_str,
            },
        )

        merge_chain = prompt_template | self.llm_model | StrOutputParser()
        answer = merge_chain.invoke({"user_prompt": user_prompt})

        # Update the state with the generated answer
        state.update({self.output[0]: answer})
        return state