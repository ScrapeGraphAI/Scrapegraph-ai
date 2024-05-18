"""
KnowledgeGraphNode Module
"""

# Imports from standard library
from typing import List, Optional
from tqdm import tqdm

# Imports from Langchain
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# Imports from the library
from .base_node import BaseNode
from ..utils import create_graph, create_interactive_graph

class KnowledgeGraphNode(BaseNode):
    """
    A node responsible for generating a knowledge graph from a dictionary.

    Attributes:
        llm_model: An instance of a language model client, configured for generating answers.
        verbose (bool): A flag indicating whether to show print statements during execution.

    Args:
        input (str): Boolean expression defining the input keys needed from the state.
        output (List[str]): List of output keys to be updated in the state.
        node_config (dict): Additional configuration for the node.
        node_name (str): The unique identifier name for the node, defaulting to "GenerateAnswer".
    """

    def __init__(self, input: str, output: List[str], node_config: Optional[dict] = None,
                 node_name: str = "KnowledgeGraph"):
        super().__init__(node_name, "node", input, output, 2, node_config)

        self.llm_model = node_config["llm_model"]
        self.verbose = False if node_config is None else node_config.get(
            "verbose", False)

    def execute(self, state: dict) -> dict:
        """
        Executes the node's logic to create a knowledge graph from a dictionary.

        Args:
            state (dict): The current state of the graph. The input keys will be used
                            to fetch the correct data from the state.

        Returns:
            dict: The updated state with the output key containing the generated answer.

        Raises:
            KeyError: If the input keys are not found in the state, indicating
                      that the necessary information for generating an answer is missing.
        """

        if self.verbose:
            print(f"--- Executing {self.node_name} Node ---")

        # Interpret input keys based on the provided input expression
        input_keys = self.get_input_keys(state)

        # Fetching data from the state based on the input keys
        input_data = [state[key] for key in input_keys]

        user_prompt = input_data[0]
        answer_dict = input_data[1]

        # Build the graph
        graph = create_graph(answer_dict)
        # Create the interactive graph
        create_interactive_graph(graph, output_file='knowledge_graph.html')

        # output_parser = JsonOutputParser()
        # format_instructions = output_parser.get_format_instructions()

        # template_merge = """
        # You are a website scraper and you have just scraped some content from multiple websites.\n
        # You are now asked to provide an answer to a USER PROMPT based on the content you have scraped.\n
        # You need to merge the content from the different websites into a single answer without repetitions (if there are any). \n
        # The scraped contents are in a JSON format and you need to merge them based on the context and providing a correct JSON structure.\n
        # OUTPUT INSTRUCTIONS: {format_instructions}\n
        # USER PROMPT: {user_prompt}\n
        # WEBSITE CONTENT: {website_content}
        # """

        # prompt_template = PromptTemplate(
        #     template=template_merge,
        #     input_variables=["user_prompt"],
        #     partial_variables={
        #         "format_instructions": format_instructions,
        #         "website_content": answers_str,
        #     },
        # )

        # merge_chain = prompt_template | self.llm_model | output_parser
        # answer = merge_chain.invoke({"user_prompt": user_prompt})

        # Update the state with the generated answer
        state.update({self.output[0]: graph})
        return state
