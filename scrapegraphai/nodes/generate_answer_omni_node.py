"""
GenerateAnswerNode Module
"""
from typing import List, Optional
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableParallel
from langchain_openai import ChatOpenAI
from langchain_mistralai import ChatMistralAI
from tqdm import tqdm
from langchain_community.chat_models import ChatOllama
from .base_node import BaseNode
from ..utils.output_parser import get_structured_output_parser, get_pydantic_output_parser
from ..prompts.generate_answer_node_omni_prompts import (TEMPLATE_NO_CHUNKS_OMNI, 
                                                        TEMPLATE_CHUNKS_OMNI,
                                                        TEMPLATE_MERGE_OMNI)

class GenerateAnswerOmniNode(BaseNode):
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

    def __init__(
        self,
        input: str,
        output: List[str],
        node_config: Optional[dict] = None,
        node_name: str = "GenerateAnswerOmni",
    ):
        super().__init__(node_name, "node", input, output, 3, node_config)

        self.llm_model = node_config["llm_model"]
        if isinstance(node_config["llm_model"], ChatOllama):
            self.llm_model.format="json"

        self.verbose = (
            False if node_config is None else node_config.get("verbose", False)
        )

        self.additional_info = node_config.get("additional_info")

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

        self.logger.info(f"--- Executing {self.node_name} Node ---")

        input_keys = self.get_input_keys(state)

        input_data = [state[key] for key in input_keys]

        user_prompt = input_data[0]
        doc = input_data[1]
        imag_desc = input_data[2]

        if self.node_config.get("schema", None) is not None:

            if isinstance(self.llm_model, (ChatOpenAI, ChatMistralAI)):
                self.llm_model = self.llm_model.with_structured_output(
                    schema = self.node_config["schema"])

                output_parser = get_structured_output_parser(self.node_config["schema"])
                format_instructions = "NA"
            else:
                output_parser = get_pydantic_output_parser(self.node_config["schema"])
                format_instructions = output_parser.get_format_instructions()

        else:
            output_parser = JsonOutputParser()
            format_instructions = output_parser.get_format_instructions()

        TEMPLATE_NO_CHUNKS_OMNI_prompt = TEMPLATE_NO_CHUNKS_OMNI
        TEMPLATE_CHUNKS_OMNI_prompt = TEMPLATE_CHUNKS_OMNI
        TEMPLATE_MERGE_OMNI_prompt= TEMPLATE_MERGE_OMNI

        if self.additional_info is not None:
            TEMPLATE_NO_CHUNKS_OMNI_prompt = self.additional_info + TEMPLATE_NO_CHUNKS_OMNI_prompt
            TEMPLATE_CHUNKS_OMNI_prompt = self.additional_info + TEMPLATE_CHUNKS_OMNI_prompt
            TEMPLATE_MERGE_OMNI_prompt = self.additional_info + TEMPLATE_MERGE_OMNI_prompt

        chains_dict = {}
        if len(doc) == 1:
            prompt = PromptTemplate(
                template=TEMPLATE_NO_CHUNKS_OMNI_prompt,
                input_variables=["question"],
                partial_variables={
                    "context": doc,
                    "format_instructions": format_instructions,
                    "img_desc": imag_desc,
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
                    template=TEMPLATE_CHUNKS_OMNI_prompt,
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
                template = TEMPLATE_MERGE_OMNI_prompt,
                input_variables=["context", "question"],
                partial_variables={"format_instructions": format_instructions},
            )

        merge_chain = merge_prompt | self.llm_model | output_parser
        answer = merge_chain.invoke({"context": batch_results, "question": user_prompt})

        state.update({self.output[0]: answer})
        return state
