"""
ParseNode Module
"""
from typing import List, Optional, Any
import tiktoken
from semchunk import chunk
from langchain_community.document_transformers import Html2TextTransformer
from langchain_core.documents import Document
from langchain_ollama import ChatOllama
from transformers import AutoTokenizer
from langchain_mistralai import ChatMistralAI
from google.generativeai import genai
from langchain_openai import ChatOpenAI
from ..utils.logging import get_logger
from ..helpers import models_tokens
from ..utils.tokenizer_openai import num_tokens_openai
from .base_node import BaseNode

class ParseNode(BaseNode):
    """
    A node responsible for parsing HTML content from a document.
    The parsed content is split into chunks for further processing.

    This node enhances the scraping workflow by allowing for targeted extraction of
    content, thereby optimizing the processing of large HTML documents.

    Attributes:
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
            node_name: str = "Parse",
        ):
        super().__init__(node_name, "node", input, output, 1, node_config)

        self.verbose = (
            False if node_config is None else node_config.get("verbose", False)
        )
        self.parse_html = (
            True if node_config is None else node_config.get("parse_html", True)
        )

        self.llm_model = node_config.get("llm_model")

    def execute(self, state: dict) -> dict:
        """
        Executes the node's logic to parse the HTML document content and split it into chunks.

        Args:
            state (dict): The current state of the graph. The input keys will be used to fetch the
                            correct data from the state.

        Returns:
            dict: The updated state with the output key containing the parsed content chunks.

        Raises:
            KeyError: If the input keys are not found in the state, indicating that the
                        necessary information for parsing the content is missing.
        """

        self.logger.info(f"--- Executing {self.node_name} Node ---")

        # Interpret input keys based on the provided input expression
        input_keys = self.get_input_keys(state)

        # Fetching data from the state based on the input keys
        input_data = [state[key] for key in input_keys]
        # Parse the document
        docs_transformed = input_data[0]
        if self.parse_html:
            docs_transformed = Html2TextTransformer().transform_documents(input_data[0])
            docs_transformed = docs_transformed[0]

            if self.llm_model is None:
                raise ValueError("llm_model cannot be None")

            if isinstance(self.llm_model, ChatOpenAI):
                num_tokens = num_tokens_openai(docs_transformed.page_content)
                context_window = models_tokens[self.llm_model.name.split("/")[0]][self.llm_model.name.split("/")[1]]

                chunks = []
                num_chunks = num_tokens // context_window

                if num_tokens % context_window != 0:
                    num_chunks += 1

                for i in range(num_chunks):
                    start = i * context_window
                    end = (i + 1) * context_window
                    chunks.append(docs_transformed.page_content[start:end])

            elif isinstance(self.llm_model, ChatMistralAI):
                print("mistral")
            elif isinstance(self.llm_model, ChatOllama):
                tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B")
                tokens = tokenizer.tokenize(docs_transformed.page_conten)
                num_tokens = len(tokens)
            #google genai
            elif isinstance(self.llm_model, str):
                model = genai.GenerativeModel(self.llm_model)
                num_tokens = model.count_tokens(docs_transformed.page_content)

                # Get the context window size for the model
                context_window = model.context_window

                chunks = []
                num_chunks = num_tokens // context_window

                if num_tokens % context_window != 0:
                    num_chunks += 1

                for i in range(num_chunks):
                    start = i * context_window
                    end = (i + 1) * context_window
                    chunks.append(docs_transformed.page_content[start:end])
            else:
                chunks = chunk(text=docs_transformed.page_content,
                            chunk_size=self.node_config.get("chunk_size", 4096)-250,
                            token_counter=lambda text: len(text.split()),
                            memoize=False)

        else:
            docs_transformed = docs_transformed[0]

            if isinstance(docs_transformed, Document):
                chunks = chunk(text=docs_transformed.page_content,
                            chunk_size=self.node_config.get("chunk_size", 4096)-250,
                            token_counter=lambda text: len(text.split()),
                            memoize=False)
            else:

                chunks = chunk(text=docs_transformed,
                                chunk_size=self.node_config.get("chunk_size", 4096)-250,
                                token_counter=lambda text: len(text.split()),
                                memoize=False)

        state.update({self.output[0]: chunks})

        return state
