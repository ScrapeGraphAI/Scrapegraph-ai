"""
GetProbableTagsNode Module
"""

from typing import List, Optional
from langchain.output_parsers import CommaSeparatedListOutputParser
from langchain.prompts import PromptTemplate
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

    def __init__(self, input: str, output: List[str], model_config: dict,
                 node_name: str = "GetProbableTags"):
        super().__init__(node_name, "node", input, output, 2, model_config)

        self.llm_model = model_config["llm_model"]

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

        print(f"--- Executing {self.node_name} Node ---")

        # Interpret input keys based on the provided input expression
        input_keys = self.get_input_keys(state)

        # Fetching data from the state based on the input keys
        input_data = [state[key] for key in input_keys]

        user_prompt = input_data[0]
        url = input_data[1]

        output_parser = CommaSeparatedListOutputParser()
        format_instructions = output_parser.get_format_instructions()

        template = """
        PROMPT:
        You are a website scraper that knows all the types of html tags.
        You are now asked to list all the html tags where you think you can find the information of the asked question.\n 
        INSTRUCTIONS: {format_instructions} \n  
        WEBPAGE: The webpage is: {webpage} \n 
        QUESTION: The asked question is the following: {question}
        """

        tag_prompt = PromptTemplate(
            template=template,
            input_variables=["question"],
            partial_variables={
                "format_instructions": format_instructions, "webpage": url},
        )

        # Execute the chain to get probable tags
        tag_answer = tag_prompt | self.llm_model | output_parser
        probable_tags = tag_answer.invoke({"question": user_prompt})

        # Update the dictionary with probable tags
        state.update({self.output[0]: probable_tags})
        return state
