"""
GenerateAnswerNode Module
"""

# Imports from standard library
from typing import List, Optional
from tqdm import tqdm

# Imports from Langchain
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableParallel

# Imports from the library
from .base_node import BaseNode
from ..helpers import template_chunks, template_no_chunks, template_merge, template_chunks_with_schema, template_no_chunks_with_schema

class GenerateAnswerNode(BaseNode):
    """
    A node that generates an answer using a large language model (LLM) based on the user's input
    and the content extracted from a webpage. It constructs a prompt from the user's input
    and the scraped content, feeds it to the LLM, and parses the LLM's response to produce
    an answer.

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
                 node_name: str = "GenerateAnswer"):

        super().__init__(node_name, "node", input, output, 2, node_config)

        self.llm_model = node_config["llm_model"]
        self.verbose = False if node_config is None else node_config.get(
            "verbose", False)

    def execute(self, state: dict) -> dict:
        """
        Generates an answer by constructing a prompt from the user's input and the scraped
        content, querying the language model, and parsing its response.

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
        doc = input_data[1]

        output_parser = JsonOutputParser()
        format_instructions = output_parser.get_format_instructions()

        chains_dict = {}

        # Use tqdm to add progress bar
        for i, chunk in enumerate(tqdm(doc, desc="Processing chunks", disable=not self.verbose)):
            if self.node_config["schema"] is None and len(doc) == 1:
                prompt = PromptTemplate(
                    template=template_no_chunks,
                    input_variables=["question"],
                    partial_variables={"context": chunk.page_content,
                                       "format_instructions": format_instructions})
            elif self.node_config["schema"] is not None and len(doc) == 1:
                 prompt = PromptTemplate(
                    template=template_no_chunks_with_schema,
                    input_variables=["question"],
                    partial_variables={"context": chunk.page_content,
                                       "format_instructions": format_instructions,
                                       "schema": self.node_config["schema"]
                                       })
            elif self.node_config["schema"] is None and len(doc) > 1:
                prompt = PromptTemplate(
                    template=template_chunks,
                    input_variables=["question"],
                    partial_variables={"context": chunk.page_content,
                                        "chunk_id": i + 1,
                                        "format_instructions": format_instructions})
            elif self.node_config["schema"] is not None and len(doc) > 1:
                prompt = PromptTemplate(
                    template=template_chunks_with_schema,
                    input_variables=["question"],
                    partial_variables={"context": chunk.page_content,
                                        "chunk_id": i + 1,
                                        "format_instructions": format_instructions,
                                        "schema": self.node_config["schema"]})

            # Dynamically name the chains based on their index
            chain_name = f"chunk{i+1}"
            chains_dict[chain_name] = prompt | self.llm_model | output_parser

        if len(chains_dict) > 1:
            # Use dictionary unpacking to pass the dynamically named chains to RunnableParallel
            map_chain = RunnableParallel(**chains_dict)
            # Chain
            answer = map_chain.invoke({"question": user_prompt})
            # Merge the answers from the chunks
            merge_prompt = PromptTemplate(
                template=template_merge,
                input_variables=["context", "question"],
                partial_variables={"format_instructions": format_instructions},
            )
            merge_chain = merge_prompt | self.llm_model | output_parser
            answer = merge_chain.invoke(
                {"context": answer, "question": user_prompt})
        else:
            # Chain
            single_chain = list(chains_dict.values())[0]
            answer = single_chain.invoke({"question": user_prompt})

        # Update the state with the generated answer
        state.update({self.output[0]: answer})
        return state
