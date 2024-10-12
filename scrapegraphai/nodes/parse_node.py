"""
ParseNode Module
"""
import re
from typing import List, Optional, Tuple
from urllib.parse import urljoin
from langchain_community.document_transformers import Html2TextTransformer
from langchain_core.documents import Document
from .base_node import BaseNode
from ..utils.split_text_into_chunks import split_text_into_chunks
from ..helpers import default_filters

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
        node_name: str = "ParseNode",
    ):
        super().__init__(node_name, "node", input, output, 1, node_config)

        self.verbose = (
            False if node_config is None else node_config.get("verbose", False)
        )
        self.parse_html = (
            True if node_config is None else node_config.get("parse_html", True)
        )
        self.parse_urls = (
            False if node_config is None else node_config.get("parse_urls", False)
        )

        self.llm_model = node_config.get("llm_model")
        self.chunk_size = node_config.get("chunk_size")

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

        if self.parse_html:
            docs_transformed = Html2TextTransformer(ignore_links=False).transform_documents(input_data[0])
            docs_transformed = docs_transformed[0]

            link_urls, img_urls = self._extract_urls(docs_transformed.page_content, source)

            chunks = split_text_into_chunks(text=docs_transformed.page_content,
                                            chunk_size=self.chunk_size-250, model=self.llm_model)
        else:
            docs_transformed = docs_transformed[0]

            try:
                link_urls, img_urls = self._extract_urls(docs_transformed.page_content, source)
            except Exception as e:
                link_urls, img_urls = "", ""

            chunk_size = self.chunk_size
            chunk_size = min(chunk_size - 500, int(chunk_size * 0.8))

            if isinstance(docs_transformed, Document):
                chunks = split_text_into_chunks(text=docs_transformed.page_content,
                                                chunk_size=chunk_size,
                                                model=self.llm_model)
            else:
                chunks = split_text_into_chunks(text=docs_transformed,
                                                chunk_size=chunk_size,
                                                model=self.llm_model)

        state.update({self.output[0]: chunks})
        if self.parse_urls:
            state.update({self.output[1]: link_urls})
            state.update({self.output[2]: img_urls})

        return state

    def _extract_urls(self, text: str, source: str) -> Tuple[List[str], List[str]]:
        """
        Extracts URLs from the given text.

        Args:
            text (str): The text to extract URLs from.

        Returns:
            Tuple[List[str], List[str]]: A tuple containing the extracted link URLs and image URLs.
        """
        if not self.parse_urls:
            return [], []

        image_extensions = default_filters.filter_dict["img_exts"]
        image_extension_seq = '|'.join(image_extensions).replace('.','')
        url_pattern = re.compile(r'(https?://[^\s]+|\S+\.(?:' + image_extension_seq + '))')

        all_urls = url_pattern.findall(text)
        all_urls = self._clean_urls(all_urls)

        if not source.startswith("http"):
            all_urls = [url for url in all_urls if url.startswith("http")]
        else:
            all_urls = [urljoin(source, url) for url in all_urls]

        images = [url for url in all_urls if any(url.endswith(ext) for ext in image_extensions)]
        links = [url for url in all_urls if url not in images]

        return links, images

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
            url = re.sub(r'.*?\]\(', '', url)
            url = url.rstrip(').')

            cleaned_urls.append(url)

        return cleaned_urls
