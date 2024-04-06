"""
Module for generating the answer node
"""
from typing import List
from langchain.output_parsers import CommaSeparatedListOutputParser
from langchain.prompts import PromptTemplate
from ..utils.research_web import search_on_web
from .base_node import BaseNode


class SearchInternetNode(BaseNode):
    """
    A node that generates an answer by querying a language model (LLM) based on the user's input
    and the content extracted from a webpage. It constructs a prompt from the user's input
    and the scraped content, feeds it to the LLM, and parses the LLM's response to produce
    an answer.

    Attributes:
        node_name (str): The unique identifier name for the node.
        node_type (str): The type of the node, set to "node" indicating a standard operational node.
        input (str): The user input used to construct the prompt.
        output (List[str]): The keys in the state dictionary 
                            where the generated answer will be stored.
        model_config (dict): Configuration parameters for the language model client.

    Args:
        input (str): The user input used to construct the prompt.
        output (List[str]): The keys in the state dictionary where the
                             generated answer will be stored.
        model_config (dict): Configuration parameters for the language model client.
        node_name (str, optional): The unique identifier name for the node. 
        Defaults to "GenerateAnswer".

    Methods:
        execute(state): Processes the input and document from the state to generate an answer,
                        updating the state with the generated answer under the 'answer' key.
    """

    def __init__(self, input: str, output: List[str], model_config: dict,
                 node_name: str = "SearchInternet"):
        """
        Initializes the SearchInternetNode with input, output, model configuration, and a node name.
        Args:
            input (str): The user input used to construct the prompt.
            output (List[str]): The keys in the state dictionary where the
             generated answer will be stored.
            model_config (dict): Configuration parameters for the language model client.
            node_name (str): The unique identifier name for the node.
        """
        super().__init__(node_name, "node", input, output, 1, model_config)
        self.llm_model = model_config["llm_model"]

    def execute(self, state):
        """
        Generates an answer by constructing a prompt from the user's input and the scraped
        content, querying the language model, and parsing its response.

        The method updates the state with the generated answer under the 'answer' key.

        Args:
            state (dict): The current state of the graph, expected to contain 'user_input',
                          and optionally 'parsed_document' or 'relevant_chunks' within 'keys'.

        Returns:
            dict: The updated state with the 'answer' key containing the generated answer.

        Raises:
            KeyError: If 'user_input' or 'document' is not found in the state, indicating
                      that the necessary information for generating an answer is missing.
        """

        print(f"--- Executing {self.node_name} Node ---")

        input_keys = self.get_input_keys(state)

        # Fetching data from the state based on the input keys
        input_data = [state[key] for key in input_keys]

        user_prompt = input_data[0]

        output_parser = CommaSeparatedListOutputParser()

        search_template = """Given the following user prompt, return a query that can be used to search the internet for relevant information. \n
        You should return only the query string. \n
        User Prompt: {user_prompt}"""

        search_prompt = PromptTemplate(
            template=search_template,
            input_variables=["user_prompt"],
        )

        # Execute the chain to get the search query
        search_answer = search_prompt | self.llm_model | output_parser
        search_query = search_answer.invoke({"user_prompt": user_prompt})[0]

        print(f"Search Query: {search_query}")
        # TODO: handle multiple URLs
        answer = search_on_web(query=search_query, search_engine="DuckDuckGo", max_results=1)[0]

        # Update the state with the generated answer
        state.update({self.output[0]: answer})
        return state
