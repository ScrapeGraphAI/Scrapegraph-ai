"""
GenerateAnswerNode Module
"""

import json
import time
from typing import List, Optional

from langchain_core.prompts import PromptTemplate
from langchain_aws import ChatBedrock
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableParallel
from langchain_openai import ChatOpenAI
from requests.exceptions import Timeout
from tqdm import tqdm

from ..prompts import (
    TEMPLATE_CHUNKS,
    TEMPLATE_CHUNKS_MD,
    TEMPLATE_MERGE,
    TEMPLATE_MERGE_MD,
    TEMPLATE_NO_CHUNKS,
    TEMPLATE_NO_CHUNKS_MD,
)
from ..utils.output_parser import get_pydantic_output_parser
from .base_node import BaseNode


class GenerateAnswerNode(BaseNode):
    """
    Initializes the GenerateAnswerNode class.

    Args:
        input (str): The input data type for the node.
        output (List[str]): The output data type(s) for the node.
        node_config (Optional[dict]): Configuration dictionary for the node,
        which includes the LLM model, verbosity, schema, and other settings.
        Defaults to None.
        node_name (str): The name of the node. Defaults to "GenerateAnswer".

    Attributes:
        llm_model: The language model specified in the node configuration.
        verbose (bool): Whether verbose mode is enabled.
        force (bool): Whether to force certain behaviors, overriding defaults.
        script_creator (bool): Whether the node is in script creation mode.
        is_md_scraper (bool): Whether the node is scraping markdown data.
        additional_info (Optional[str]): Any additional information to be
        included in the prompt templates.
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

        if isinstance(node_config["llm_model"], ChatOllama):
            if node_config.get("schema", None) is None:
                self.llm_model.format = "json"
            else:
                self.llm_model.format = self.node_config["schema"].model_json_schema()

        self.verbose = node_config.get("verbose", False)
        self.force = node_config.get("force", False)
        self.script_creator = node_config.get("script_creator", False)
        self.is_md_scraper = node_config.get("is_md_scraper", False)
        self.additional_info = node_config.get("additional_info")
        self.timeout = node_config.get("timeout", 480)

    def invoke_with_timeout(self, chain, inputs, timeout):
        """Helper method to invoke chain with timeout"""
        try:
            start_time = time.time()
            response = chain.invoke(inputs)
            if time.time() - start_time > timeout:
                raise Timeout(f"Response took longer than {timeout} seconds")
            return response
        except Timeout as e:
            self.logger.error(f"Timeout error: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Error during chain execution: {str(e)}")
            raise

    def process(self, state: dict) -> dict:
        """Process the input state and generate an answer."""
        user_prompt = state.get("user_prompt")
        # Check for content in different possible state keys
        content = (
            state.get("relevant_chunks")
            or state.get("parsed_doc")
            or state.get("doc")
            or state.get("content")
        )

        if not content:
            raise ValueError("No content found in state to generate answer from")

        if not user_prompt:
            raise ValueError("No user prompt found in state")

        # Create the chain input with both content and question keys
        chain_input = {"content": content, "question": user_prompt}

        try:
            response = self.invoke_with_timeout(self.chain, chain_input, self.timeout)
            state.update({self.output[0]: response})
            return state
        except Exception as e:
            self.logger.error(f"Error in GenerateAnswerNode: {str(e)}")
            raise

    def execute(self, state: dict) -> dict:
        """
        Executes the GenerateAnswerNode.

        Args:
            state (dict): The current state of the graph. The input keys will be used
                          to fetch the correct data from the state.

        Returns:
            dict: The updated state with the output key containing the generated answer.
        """
        self.logger.info(f"--- Executing {self.node_name} Node ---")

        input_keys = self.get_input_keys(state)
        input_data = [state[key] for key in input_keys]
        user_prompt = input_data[0]
        doc = input_data[1]

        if self.node_config.get("schema", None) is not None:
            if isinstance(self.llm_model, ChatOpenAI):
                output_parser = get_pydantic_output_parser(self.node_config["schema"])
                format_instructions = output_parser.get_format_instructions()
            else:
                if not isinstance(self.llm_model, ChatBedrock):
                    output_parser = get_pydantic_output_parser(
                        self.node_config["schema"]
                    )
                    format_instructions = output_parser.get_format_instructions()
                else:
                    output_parser = None
                    format_instructions = ""
        else:
            if not isinstance(self.llm_model, ChatBedrock):
                output_parser = JsonOutputParser()
                format_instructions = (
                    "You must respond with a JSON object. Your response should be formatted as a valid JSON "
                    "with a 'content' field containing your analysis. For example:\n"
                    '{{"content": "your analysis here"}}'
                )
            else:
                output_parser = None
                format_instructions = ""

        if (
            not self.script_creator
            or self.force
            and not self.script_creator
            or self.is_md_scraper
        ):
            template_no_chunks_prompt = TEMPLATE_NO_CHUNKS_MD
            template_chunks_prompt = TEMPLATE_CHUNKS_MD
            template_merge_prompt = TEMPLATE_MERGE_MD
        else:
            template_no_chunks_prompt = TEMPLATE_NO_CHUNKS
            template_chunks_prompt = TEMPLATE_CHUNKS
            template_merge_prompt = TEMPLATE_MERGE

        if self.additional_info is not None:
            template_no_chunks_prompt = self.additional_info + template_no_chunks_prompt
            template_chunks_prompt = self.additional_info + template_chunks_prompt
            template_merge_prompt = self.additional_info + template_merge_prompt

        if len(doc) == 1:
            prompt = PromptTemplate(
                template=template_no_chunks_prompt,
                input_variables=["content", "question"],
                partial_variables={
                    "format_instructions": format_instructions,
                },
            )
            chain = prompt | self.llm_model
            if output_parser:
                chain = chain | output_parser

            try:
                answer = self.invoke_with_timeout(
                    chain, {"content": doc, "question": user_prompt}, self.timeout
                )
            except (Timeout, json.JSONDecodeError) as e:
                error_msg = (
                    "Response timeout exceeded"
                    if isinstance(e, Timeout)
                    else "Invalid JSON response format"
                )
                state.update(
                    {self.output[0]: {"error": error_msg, "raw_response": str(e)}}
                )
                return state

            state.update({self.output[0]: answer})
            return state

        chains_dict = {}
        for i, chunk in enumerate(
            tqdm(doc, desc="Processing chunks", disable=not self.verbose)
        ):
            prompt = PromptTemplate(
                template=template_chunks_prompt,
                input_variables=["question"],
                partial_variables={
                    "content": chunk,
                    "chunk_id": i + 1,
                    "format_instructions": format_instructions,
                },
            )
            chain_name = f"chunk{i + 1}"
            chains_dict[chain_name] = prompt | self.llm_model
            if output_parser:
                chains_dict[chain_name] = chains_dict[chain_name] | output_parser

        async_runner = RunnableParallel(**chains_dict)
        try:
            batch_results = self.invoke_with_timeout(
                async_runner, {"question": user_prompt}, self.timeout
            )
        except (Timeout, json.JSONDecodeError) as e:
            error_msg = (
                "Response timeout exceeded during chunk processing"
                if isinstance(e, Timeout)
                else "Invalid JSON response format in chunk processing"
            )
            state.update({self.output[0]: {"error": error_msg, "raw_response": str(e)}})
            return state

        merge_prompt = PromptTemplate(
            template=template_merge_prompt,
            input_variables=["content", "question"],
            partial_variables={"format_instructions": format_instructions},
        )

        merge_chain = merge_prompt | self.llm_model
        if output_parser:
            merge_chain = merge_chain | output_parser
        try:
            answer = self.invoke_with_timeout(
                merge_chain,
                {"content": batch_results, "question": user_prompt},
                self.timeout,
            )
        except (Timeout, json.JSONDecodeError) as e:
            error_msg = (
                "Response timeout exceeded during merge"
                if isinstance(e, Timeout)
                else "Invalid JSON response format during merge"
            )
            state.update({self.output[0]: {"error": error_msg, "raw_response": str(e)}})
            return state

        state.update({self.output[0]: answer})
        return state
