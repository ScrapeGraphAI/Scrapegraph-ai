"""
ParseNode Module
"""
from typing import Tuple, List, Optional
from urllib.parse import urljoin
from semchunk import chunk
from langchain_community.document_transformers import Html2TextTransformer
from langchain_core.documents import Document
from .base_node import BaseNode
from ..helpers import default_filters

import re

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
        self.llm_model = node_config['llm_model']
        self.parse_urls = (
            False if node_config is None else node_config.get("parse_urls", False)
        )

    def _clean_urls(self, urls: List[str]) -> List[str]:
        """
        Cleans the URLs extracted from the text.

        Args:
            urls (List[str]): The list of URLs to clean.

        Returns:
            List[str]: The cleaned URLs.
        """
        cleaned_urls = []
        for url in urls:
            # Remove any leading 'thumbnail](' or similar patterns
            url = re.sub(r'.*?\]\(', '', url)
            
            # Remove any trailing parentheses or brackets
            url = url.rstrip(').')
            
            cleaned_urls.append(url)
        
        return cleaned_urls

    def extract_urls(self, text: str, source: str) -> Tuple[List[str], List[str]]:
        """
        Extracts URLs from the given text.

        Args:
            text (str): The text to extract URLs from.

        Returns:
            Tuple[List[str], List[str]]: A tuple containing the extracted link URLs and image URLs.
        """
        # Return empty lists if the URLs are not to be parsed
        if not self.parse_urls:
            return [], []
        
        # Regular expression to find URLs (both links and images)
        image_extensions = default_filters.filter_dict["img_exts"]
        image_extension_seq = '|'.join(image_extensions).replace('.','')
        url_pattern = re.compile(r'(https?://[^\s]+|\S+\.(?:' + image_extension_seq + '))')

        # Find all URLs in the string
        all_urls = url_pattern.findall(text)
        all_urls = self._clean_urls(all_urls)

        if not source.startswith("http"):
            # Remove any URLs that is not complete
            all_urls = [url for url in all_urls if url.startswith("http")]
        else:
            # Add to local URLs the source URL
            all_urls = [urljoin(source, url) for url in all_urls]
        
        images = [url for url in all_urls if any(url.endswith(ext) for ext in image_extensions)]
        links = [url for url in all_urls if url not in images]

        return links, images

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

        input_keys = self.get_input_keys(state)

        input_data = [state[key] for key in input_keys]

        docs_transformed = input_data[0]
        source = input_data[1] if self.parse_urls else None

        def count_tokens(text):
            from ..utils import token_count
            return token_count(text, self.llm_model.model_name)

        if self.parse_html:
            docs_transformed = Html2TextTransformer().transform_documents(input_data[0])
            docs_transformed = docs_transformed[0]

            link_urls, img_urls = self.extract_urls(docs_transformed.page_content, source)

            chunks = chunk(text=docs_transformed.page_content,
                            chunk_size=self.node_config.get("chunk_size", 4096)-250,
                            token_counter=count_tokens,
                            memoize=False)
        else:
            docs_transformed = docs_transformed[0]

            link_urls, img_urls = self.extract_urls(docs_transformed.page_content, source)

            chunk_size = self.node_config.get("chunk_size", 4096)
            chunk_size = min(chunk_size - 500, int(chunk_size * 0.9))

            if isinstance(docs_transformed, Document):
                chunks = chunk(text=docs_transformed.page_content,
                            chunk_size=chunk_size,
                            token_counter=count_tokens,
                            memoize=False)
            else:
                chunks = chunk(text=docs_transformed,
                                chunk_size=chunk_size,
                                token_counter=count_tokens,
                                memoize=False)

        state.update({self.output[0]: chunks})
        if self.parse_urls:
            state.update({self.output[1]: link_urls})
            state.update({self.output[2]: img_urls})

        return state
