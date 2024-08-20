"""
Generate answer_node
"""
import re
import json
from typing import List, Optional
import requests
from tqdm import tqdm
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableParallel
from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatOllama
from ..utils.logging import get_logger
from ..utils import parse_response_to_dict
from .base_node import BaseNode
from ..prompts import (
    TEMPLATE_CHUNKS, TEMPLATE_NO_CHUNKS, TEMPLATE_MERGE,
    TEMPLATE_CHUNKS_MD, TEMPLATE_NO_CHUNKS_MD, TEMPLATE_MERGE_MD
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

        self.llm_model = node_config.get("llm_model")
        if isinstance(self.llm_model, ChatOllama):
            self.llm_model.format = "json"

        self.verbose = node_config.get("verbose", False)
        self.force = node_config.get("force", False)
        self.script_creator = node_config.get("script_creator", False)
        self.is_md_scraper = node_config.get("is_md_scraper", False)
        self.additional_info = node_config.get("additional_info", "")
        self.api_key = node_config.get("config", {}).get("llm", {}).get("api_key", "")



    def execute(self, state: dict) -> dict:
        self.logger.info(f"--- Executing {self.node_name} Node ---")

        input_keys = self.get_input_keys(state)
        user_prompt, doc = [state[key] for key in input_keys]

        schema = self.node_config.get("schema")
        output_parser = JsonOutputParser(pydantic_object=schema) if schema else JsonOutputParser()
        format_instructions = output_parser.get_format_instructions()

        if isinstance(self.llm_model, ChatOpenAI) and (not self.script_creator or self.force) or self.is_md_scraper:
            templates = {
                'no_chunks': TEMPLATE_NO_CHUNKS_MD,
                'chunks': TEMPLATE_CHUNKS_MD,
                'merge': TEMPLATE_MERGE_MD
            }

            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }

            if len(doc) == 1:
                prompt = templates['no_chunks'].format(
                    question=user_prompt,
                    context=doc[0],
                    format_instructions=format_instructions
                )
                response = requests.post(url, headers=headers, json={
                    "model": self.llm_model.model_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0
                }, timeout=10)

                response_text = response.json()['choices'][0]['message']['content']
                cleaned_response = parse_response_to_dict(response_text)
                state.update({self.output[0]: cleaned_response})
                return state

            chunks_responses = []
            for i, chunk in enumerate(
                tqdm(doc, desc="Processing chunks",
                     disable=not self.verbose)):
                prompt = templates['chunks'].format(
                    question=user_prompt,
                    context=chunk,
                    chunk_id=i + 1,
                    format_instructions=format_instructions
                )
                response = requests.post(url, headers=headers, json={
                    "model": self.llm_model.model_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0
                }, timeout=10)
                chunk_response = response.json()['choices'][0]['message']['content']
                cleaned_chunk_response = parse_response_to_dict(chunk_response)
                chunks_responses.append(cleaned_chunk_response)

            merge_context = " ".join([json.dumps(chunk) for chunk in chunks_responses])
            merge_prompt = templates['merge'].format(
                question=user_prompt,
                context=merge_context,
                format_instructions=format_instructions
            )
            response = requests.post(url, headers=headers, json={
                "model": self.llm_model.model_name,
                "messages": [{"role": "user", "content": merge_prompt}],
                "temperature": 0
            }, timeout=10)
            response_text = response.json()['choices'][0]['message']['content']
            cleaned_response = parse_response_to_dict(response_text)
            state.update({self.output[0]: cleaned_response})
            return state

        else:
            templates = {
                'no_chunks': TEMPLATE_NO_CHUNKS,
                'chunks': TEMPLATE_CHUNKS,
                'merge': TEMPLATE_MERGE
            }

            if self.additional_info:
                templates = {key: self.additional_info + template for key, template in templates.items()}

            if len(doc) == 1:
                prompt = PromptTemplate(
                    template=templates['no_chunks'],
                    input_variables=["question"],
                    partial_variables={"context": doc, "format_instructions": format_instructions}
                )
                chain = prompt | self.llm_model | output_parser
                answer = chain.invoke({"question": user_prompt})
                state.update({self.output[0]: answer})
                return state

            chains_dict = {}
            for i, chunk in enumerate(tqdm(doc, 
                                           desc="Processing chunks", 
                                           disable=not self.verbose)):
                prompt = PromptTemplate(
                    template=templates['chunks'],
                    input_variables=["question"],
                    partial_variables={"context": chunk, "chunk_id": i + 1,
                                       "format_instructions": format_instructions}
                )
                chain_name = f"chunk{i+1}"
                chains_dict[chain_name] = prompt | self.llm_model | output_parser

            async_runner = RunnableParallel(**chains_dict)
            batch_results = async_runner.invoke({"question": user_prompt})

            merge_prompt = PromptTemplate(
                template=templates['merge'],
                input_variables=["context", "question"],
                partial_variables={"format_instructions": format_instructions}
            )
            merge_chain = merge_prompt | self.llm_model | output_parser
            answer = merge_chain.invoke({"context": batch_results, "question": user_prompt})

            state.update({self.output[0]: answer})
            return state
