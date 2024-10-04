"""
DescriptionNode Module
"""
from typing import List, Optional
from tqdm import tqdm
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel
from .base_node import BaseNode
from ..prompts.description_node_prompts import DESCRIPTION_NODE_PROMPT

class DescriptionNode(BaseNode):
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
        node_name: str = "DESCRIPTION",
    ):
        super().__init__(node_name, "node", input, output, 2, node_config)
        self.llm_model = node_config["llm_model"]
        self.verbose = (
            False if node_config is None else node_config.get("verbose", False)
        )
        self.cache_path = node_config.get("cache_path", False)

    def execute(self, state: dict) -> dict:
        self.logger.info(f"--- Executing {self.node_name} Node ---")

        docs = [elem for elem in state.get("docs")]

        chains_dict = {}

        for i, chunk in enumerate(tqdm(docs, desc="Processing chunks", disable=not self.verbose)):
            prompt = PromptTemplate(
                template=DESCRIPTION_NODE_PROMPT,
                partial_variables={"content": chunk.get("document")}
            )
            chain_name = f"chunk{i+1}"
            chains_dict[chain_name] = prompt | self.llm_model

        async_runner = RunnableParallel(**chains_dict)
        batch_results = async_runner.invoke({})


        for i in range(1, len(docs)+1):
            docs[i-1]["summary"] = batch_results.get(f"chunk{i}").content

        state.update({self.output[0]: docs})

        return state
