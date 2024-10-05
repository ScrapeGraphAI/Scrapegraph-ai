"""
GenerateAnswerNodeKLevel Module
"""
from typing import List, Optional
from langchain.prompts import PromptTemplate
from tqdm import tqdm
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableParallel
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langchain_mistralai import ChatMistralAI
from langchain_aws import ChatBedrock
from ..utils.output_parser import get_structured_output_parser, get_pydantic_output_parser
from .base_node import BaseNode
from ..prompts import (
    TEMPLATE_CHUNKS, TEMPLATE_NO_CHUNKS, TEMPLATE_MERGE,
    TEMPLATE_CHUNKS_MD, TEMPLATE_NO_CHUNKS_MD, TEMPLATE_MERGE_MD
)

class GenerateAnswerNodeKLevel(BaseNode):
    """
    A node responsible for compressing the input tokens and storing the document
    in a vector database for retrieval. Relevant chunks are stored in the state.

    It allows scraping of big documents without exceeding the token limit of the language model.

    Attributes:
        llm_model: An instance of a language model client, configured for generating answers.
        verbose (bool): A flag indicating whether to show print statements during execution.

    Args:
        input (str): Boolean expression defining the input keys needed from the state.
        output (List[str]): List of output keys to be updated in the state.
        node_config (dict): Additional configuration for the node.
        node_name (str): The unique identifier name for the node, defaulting to "Parse".
    """

    def __init__(
        self,
        input: str,
        output: List[str],
        node_config: Optional[dict] = None,
        node_name: str = "GANLK",
    ):
        super().__init__(node_name, "node", input, output, 2, node_config)

        self.llm_model = node_config["llm_model"]
        self.embedder_model = node_config.get("embedder_model", None)
        self.verbose = node_config.get("verbose", False)
        self.force = node_config.get("force", False)
        self.script_creator = node_config.get("script_creator", False)
        self.is_md_scraper = node_config.get("is_md_scraper", False)
        self.additional_info = node_config.get("additional_info")

    def execute(self, state: dict) -> dict:
        self.logger.info(f"--- Executing {self.node_name} Node ---")

        user_prompt = state.get("user_prompt")

        if self.node_config.get("schema", None) is not None:
            if isinstance(self.llm_model, (ChatOpenAI, ChatMistralAI)):
                self.llm_model = self.llm_model.with_structured_output(
                    schema=self.node_config["schema"]
                )
                output_parser = get_structured_output_parser(self.node_config["schema"])
                format_instructions = "NA"
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

        client = state["vectorial_db"]

        if state.get("embeddings"):
            import openai
            openai_client = openai.Client()

            answer_db = client.search(
            collection_name="collection",
            query_vector=openai_client.embeddings.create(
                input=["What is the best to use for vector search scaling?"],
                model=state.get("embeddings").get("model"),
            )
            .data[0]
            .embedding,
        )
        else:
            answer_db = client.query(
                collection_name="vectorial_collection",
                query_text=user_prompt
            )

        chains_dict = {}
        elems =[state.get("docs")[elem.id-1] for elem in answer_db if elem.score>0.5]

        for i, chunk in enumerate(tqdm(elems,
                                       desc="Processing chunks", disable=not self.verbose)):
            prompt = PromptTemplate(
                        template=template_chunks_prompt,
                        input_variables=["format_instructions"],
                        partial_variables={"context": chunk.get("document"),
                                        "chunk_id": i + 1,
                                     }
                )
            chain_name = f"chunk{i+1}"
            chains_dict[chain_name] = prompt | self.llm_model

        async_runner = RunnableParallel(**chains_dict)
        batch_results = async_runner.invoke({"format_instructions": user_prompt})

        merge_prompt = PromptTemplate(
            template=template_merge_prompt,
            input_variables=["context", "question"],
            partial_variables={"format_instructions": format_instructions}
        )

        merge_chain = merge_prompt | self.llm_model
        if output_parser:
            merge_chain = merge_chain | output_parser
        answer = merge_chain.invoke({"context": batch_results, "question": user_prompt})

        state["answer"] = answer

        return state
