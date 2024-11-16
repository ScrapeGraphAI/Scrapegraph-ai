"""
GenerateAnswerNode Module
"""
from typing import List, Optional
from json.decoder import JSONDecodeError
import time
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableParallel
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langchain_aws import ChatBedrock
from langchain_community.chat_models import ChatOllama
from tqdm import tqdm
from .base_node import BaseNode
from ..utils.output_parser import get_structured_output_parser, get_pydantic_output_parser
from requests.exceptions import Timeout
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks import get_openai_callback
from ..prompts import (
    TEMPLATE_CHUNKS, TEMPLATE_NO_CHUNKS, TEMPLATE_MERGE,
    TEMPLATE_CHUNKS_MD, TEMPLATE_NO_CHUNKS_MD, TEMPLATE_MERGE_MD
)

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
            self.llm_model.format = "json"

        self.verbose = node_config.get("verbose", False)
        self.force = node_config.get("force", False)
        self.script_creator = node_config.get("script_creator", False)
        self.is_md_scraper = node_config.get("is_md_scraper", False)
        self.additional_info = node_config.get("additional_info")
        self.timeout = node_config.get("timeout", 30)

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
                    output_parser = get_pydantic_output_parser(self.node_config["schema"])
                    format_instructions = output_parser.get_format_instructions()
                else:
                    output_parser = None
                    format_instructions = ""
        else:
            if not isinstance(self.llm_model, ChatBedrock):
                output_parser = JsonOutputParser()
                format_instructions = output_parser.get_format_instructions()
            else:
                output_parser = None
                format_instructions = ""

        if isinstance(self.llm_model, (ChatOpenAI, AzureChatOpenAI)) \
            and not self.script_creator \
            or self.force \
            and not self.script_creator or self.is_md_scraper:
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

        def invoke_with_timeout(chain, inputs, timeout):
            try:
                with get_openai_callback() as cb:
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

        if len(doc) == 1:
            prompt = PromptTemplate(
                template=template_no_chunks_prompt,
                input_variables=["question"],
                partial_variables={"context": doc, "format_instructions": format_instructions}
            )
            chain = prompt | self.llm_model
            try:
                raw_response = invoke_with_timeout(chain, {"question": user_prompt}, self.timeout)
            except Timeout:
                state.update({self.output[0]: {"error": "Response timeout exceeded"}})
                return state

            if output_parser:
                try:
                    answer = output_parser.parse(raw_response.content)
                except JSONDecodeError:
                    lines = raw_response.split('\n')
                    if lines[0].strip().startswith('```'):
                        lines = lines[1:]
                    if lines[-1].strip().endswith('```'):
                        lines = lines[:-1]
                    cleaned_response = '\n'.join(lines)
                    answer = output_parser.parse(cleaned_response)
            else:
                answer = raw_response.content

            state.update({self.output[0]: answer})
            return state

        chains_dict = {}
        for i, chunk in enumerate(tqdm(doc, desc="Processing chunks", disable=not self.verbose)):
            prompt = PromptTemplate(
                template=template_chunks_prompt,
                input_variables=["question"],
                partial_variables={"context": chunk,
                                   "chunk_id": i + 1,
                                   "format_instructions": format_instructions}
            )
            chain_name = f"chunk{i+1}"
            chains_dict[chain_name] = prompt | self.llm_model
            if output_parser:
                chains_dict[chain_name] = chains_dict[chain_name] | output_parser

        async_runner = RunnableParallel(**chains_dict)
        try:
            batch_results = invoke_with_timeout(
                async_runner, 
                {"question": user_prompt}, 
                self.timeout
            )
        except Timeout:
            state.update({self.output[0]: {"error": "Response timeout exceeded during chunk processing"}})
            return state

        merge_prompt = PromptTemplate(
            template=template_merge_prompt,
            input_variables=["context", "question"],
            partial_variables={"format_instructions": format_instructions}
        )

        merge_chain = merge_prompt | self.llm_model
        if output_parser:
            merge_chain = merge_chain | output_parser
        try:
            answer = invoke_with_timeout(
                merge_chain,
                {"context": batch_results, "question": user_prompt},
                self.timeout
            )
        except Timeout:
            state.update({self.output[0]: {"error": "Response timeout exceeded during merge"}})
            return state

        state.update({self.output[0]: answer})
        return state
