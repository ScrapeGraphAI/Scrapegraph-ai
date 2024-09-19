"""
Module for generating the answer node
"""

from typing import List, Optional
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableParallel
from langchain_openai import ChatOpenAI
from langchain_mistralai import ChatMistralAI
from tqdm import tqdm
from .base_node import BaseNode
from ..utils.output_parser import get_structured_output_parser, get_pydantic_output_parser
from ..prompts import TEMPLATE_CHUKS_CSV, TEMPLATE_NO_CHUKS_CSV, TEMPLATE_MERGE_CSV

class GenerateAnswerCSVNode(BaseNode):
    """
    A node that generates an answer using a language model (LLM) based on the user's input
    and the content extracted from a webpage. It constructs a prompt from the user's input
    and the scraped content, feeds it to the LLM, and parses the LLM's response to produce
    an answer.

    Attributes:
        llm_model: An instance of a language model client, configured for generating answers.
        node_name (str): The unique identifier name for the node, defaulting
        to "GenerateAnswerNodeCsv".
        node_type (str): The type of the node, set to "node" indicating a
        standard operational node.

    Args:
        llm_model: An instance of the language model client (e.g., ChatOpenAI) used
        for generating answers.
        node_name (str, optional): The unique identifier name for the node.
        Defaults to "GenerateAnswerNodeCsv".

    Methods:
        execute(state): Processes the input and document from the state to generate an answer,
                        updating the state with the generated answer under the 'answer' key.
    """

    def __init__(
        self,
        input: str,
        output: List[str],
        node_config: Optional[dict] = None,
        node_name: str = "GenerateAnswerCSV",
    ):
        """
        Initializes the GenerateAnswerNodeCsv with a language model client and a node name.
        Args:
            llm_model: An instance of the OpenAIImageToText class.
            node_name (str): name of the node
        """
        super().__init__(node_name, "node", input, output, 2, node_config)

        self.llm_model = node_config["llm_model"]

        self.verbose = (
            False if node_config is None else node_config.get("verbose", False)
        )

        self.additional_info = node_config.get("additional_info")

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

        self.logger.info(f"--- Executing {self.node_name} Node ---")

        # Interpret input keys based on the provided input expression
        input_keys = self.get_input_keys(state)

        # Fetching data from the state based on the input keys
        input_data = [state[key] for key in input_keys]

        user_prompt = input_data[0]
        doc = input_data[1]

        # Initialize the output parser
        if self.node_config.get("schema", None) is not None:

            if isinstance(self.llm_model, (ChatOpenAI, ChatMistralAI)):
                self.llm_model = self.llm_model.with_structured_output(
                    schema = self.node_config["schema"]) # json schema works only on specific models

                output_parser = get_structured_output_parser(self.node_config["schema"])
                format_instructions = "NA"
            else:
                output_parser = get_pydantic_output_parser(self.node_config["schema"])
                format_instructions = output_parser.get_format_instructions()

        else:
            output_parser = JsonOutputParser()
            format_instructions = output_parser.get_format_instructions()

        TEMPLATE_NO_CHUKS_CSV_PROMPT = TEMPLATE_NO_CHUKS_CSV
        TEMPLATE_CHUKS_CSV_PROMPT = TEMPLATE_CHUKS_CSV
        TEMPLATE_MERGE_CSV_PROMPT  = TEMPLATE_MERGE_CSV

        if self.additional_info is not None:
            TEMPLATE_NO_CHUKS_CSV_PROMPT = self.additional_info + TEMPLATE_NO_CHUKS_CSV
            TEMPLATE_CHUKS_CSV_PROMPT = self.additional_info + TEMPLATE_CHUKS_CSV
            TEMPLATE_MERGE_CSV_PROMPT = self.additional_info + TEMPLATE_MERGE_CSV

        chains_dict = {}

        if len(doc) == 1:
            prompt = PromptTemplate(
                template=TEMPLATE_NO_CHUKS_CSV_PROMPT,
                input_variables=["question"],
                partial_variables={
                    "context": doc,
                    "format_instructions": format_instructions,
                },
            )

            chain =  prompt | self.llm_model | output_parser
            answer = chain.invoke({"question": user_prompt})
            state.update({self.output[0]: answer})
            return state

        for i, chunk in enumerate(
            tqdm(doc, desc="Processing chunks", disable=not self.verbose)
        ):
            prompt = PromptTemplate(
                    template=TEMPLATE_CHUKS_CSV_PROMPT,
                    input_variables=["question"],
                    partial_variables={
                        "context": chunk,
                        "chunk_id": i + 1,
                        "format_instructions": format_instructions,
                    },
                )

            chain_name = f"chunk{i+1}"
            chains_dict[chain_name] = prompt | self.llm_model | output_parser

        async_runner = RunnableParallel(**chains_dict)

        batch_results =  async_runner.invoke({"question": user_prompt})

        merge_prompt = PromptTemplate(
                template = TEMPLATE_MERGE_CSV_PROMPT,
                input_variables=["context", "question"],
                partial_variables={"format_instructions": format_instructions},
            )

        merge_chain = merge_prompt | self.llm_model | output_parser
        answer = merge_chain.invoke({"context": batch_results, "question": user_prompt})

        state.update({self.output[0]: answer})
        return state
