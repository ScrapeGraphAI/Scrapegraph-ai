"""
GenerateAnswerNode Module
"""
import asyncio
from typing import List, Optional
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import AsyncRunnable
from tqdm import tqdm
from ..utils.merge_results import merge_results
from ..utils.logging import get_logger
from ..models import Ollama, OpenAI
from .base_node import BaseNode
from ..helpers import (
template_chunks, template_no_chunks, template_merge,
template_chunks_md, template_no_chunks_md, template_merge_md
)

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

    def __init__(
        self,
        input: str,
        output: List[str],
        node_config: Optional[dict] = None,
        node_name: str = "GenerateAnswer",
    ):
        super().__init__(node_name, "node", input, output, 2, node_config)
      
        self.llm_model = node_config["llm_model"]

        self.verbose = (
            True if node_config is None else node_config.get("verbose", False)
        )
        self.force = (
            False if node_config is None else node_config.get("force", False)
        )
        self.script_creator = (
            False if node_config is None else node_config.get("script_creator", False)
        )


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

        # Interpret input keys based on the provided input expression
        input_keys = self.get_input_keys(state)
        # Fetching data from the state based on the input keys
        input_data = [state[key] for key in input_keys]
        user_prompt = input_data[0]
        doc = input_data[1]

        # Initialize the output parser
        if self.node_config.get("schema", None) is not None:
            output_parser = JsonOutputParser(pydantic_object=self.node_config["schema"])
        else:
            output_parser = JsonOutputParser()

        format_instructions = output_parser.get_format_instructions()

        if isinstance(self.llm_model, OpenAI) and not self.script_creator or self.force and not self.script_creator:
            template_no_chunks_prompt = template_no_chunks_md
            template_chunks_prompt = template_chunks_md
            template_merge_prompt = template_merge_md
        else:
            template_no_chunks_prompt = template_no_chunks
            template_chunks_prompt = template_chunks
            template_merge_prompt = template_merge

        chains_dict = {}
        answers = []

        # Use tqdm to add progress bar
        for i, chunk in enumerate(tqdm(doc, desc="Processing chunks", disable=not self.verbose)):
            if len(doc) == 1:
                # No batching needed for single chunk
                prompt = PromptTemplate(
                    template=template_no_chunks,
                    input_variables=["question"],
                    partial_variables={"context": chunk.page_content,
                                    "format_instructions": format_instructions})
                chain = prompt | self.llm_model | output_parser
                answer = chain.invoke({"question": user_prompt})
                
            else:
                # Prepare prompt with chunk information
                prompt = PromptTemplate(
                    template=template_chunks,
                    input_variables=["question"],
                    partial_variables={"context": chunk.page_content,
                                    "chunk_id": i + 1,
                                    "format_instructions": format_instructions})
                # Add chain to dictionary with dynamic name
                chain_name = f"chunk{i+1}"
                chains_dict[chain_name] = prompt | self.llm_model | output_parser

            # Batch process chains if there are multiple chunks
        if len(chains_dict) > 1:
            async def process_chains():
                async_runner = AsyncRunnable()
                for chain_name, chain in chains_dict.items():
                    async_runner.add(chain.abatch([{"question": user_prompt}] * len(doc)))
                batch_results = await async_runner.run()
                return batch_results

            # Run asynchronous batch processing and get results
            loop = asyncio.get_event_loop()
            batch_answers = loop.run_until_complete(process_chains())

            # Merge batch results (assuming same structure)
            merged_answer = merge_results(answers, batch_answers)
            answers = merged_answer

        state.update({self.output[0]: answers})
        return state
