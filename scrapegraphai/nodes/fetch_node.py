""" 
FetchNode Module
"""

import json
import requests
from typing import List, Optional

import pandas as pd
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

from ..docloaders import ChromiumLoader
from .base_node import BaseNode
from ..utils.cleanup_html import cleanup_html


class FetchNode(BaseNode):
    """
    A node responsible for fetching the HTML content of a specified URL and updating
    the graph's state with this content. It uses ChromiumLoader to fetch
    the content from a web page asynchronously (with proxy protection).

    This node acts as a starting point in many scraping workflows, preparing the state
    with the necessary HTML content for further processing by subsequent nodes in the graph.

    Attributes:
        headless (bool): A flag indicating whether the browser should run in headless mode.
        verbose (bool): A flag indicating whether to print verbose output during execution.

    Args:
        input (str): Boolean expression defining the input keys needed from the state.
        output (List[str]): List of output keys to be updated in the state.
        node_config (Optional[dict]): Additional configuration for the node.
        node_name (str): The unique identifier name for the node, defaulting to "Fetch".
    """

    def __init__(
        self,
        input: str,
        output: List[str],
        node_config: Optional[dict] = None,
        node_name: str = "Fetch",
    ):
        super().__init__(node_name, "node", input, output, 1)

        self.headless = (
            True if node_config is None else node_config.get("headless", True)
        )
        self.verbose = (
            False if node_config is None else node_config.get("verbose", False)
        )
        self.useSoup = (
          False if node_config is None else node_config.get("useSoup", False)
        )
        self.loader_kwargs = (
            {} if node_config is None else node_config.get("loader_kwargs", {})
        )

    def execute(self, state):
        """
        Executes the node's logic to fetch HTML content from a specified URL and
        update the state with this content.

        Args:
            state (dict): The current state of the graph. The input keys will be used
                            to fetch the correct data types from the state.

        Returns:
            dict: The updated state with a new output key containing the fetched HTML content.

        Raises:
            KeyError: If the input key is not found in the state, indicating that the
                    necessary information to perform the operation is missing.
        """
        if self.verbose:
            print(f"--- Executing {self.node_name} Node ---")

        # Interpret input keys based on the provided input expression
        input_keys = self.get_input_keys(state)
        # Fetching data from the state based on the input keys
        input_data = [state[key] for key in input_keys]

        source = input_data[0]
        if (
            self.input == "json_dir"
            or self.input == "xml_dir"
            or self.input == "csv_dir"
        ):
            compressed_document = [
                Document(page_content=source, metadata={"source": "local_dir"})
            ]
        # if it is a local directory

        # handling for pdf
        elif self.input == "pdf":
            loader = PyPDFLoader(source)
            compressed_document = loader.load()

        elif self.input == "csv":
            compressed_document = [
                Document(
                    page_content=str(pd.read_csv(source)), metadata={"source": "csv"}
                )
            ]
        elif self.input == "json":
            f = open(source)
            compressed_document = [
                Document(page_content=str(json.load(f)), metadata={"source": "json"})
            ]
        elif self.input == "xml":
            with open(source, "r", encoding="utf-8") as f:
                data = f.read()
            compressed_document = [
                Document(page_content=data, metadata={"source": "xml"})
            ]
        elif self.input == "pdf_dir":
            pass

        elif not source.startswith("http"):
            title, minimized_body, link_urls, image_urls = cleanup_html(source, source)
            parsed_content = f"Title: {title}, Body: {minimized_body}, Links: {link_urls}, Images: {image_urls}"
            compressed_document = [Document(page_content=parsed_content,
                                            metadata={"source": "local_dir"}
                                           )]
        
        elif self.useSoup:
            response = requests.get(source)
            if response.status_code == 200:
                title, minimized_body, link_urls, image_urls = cleanup_html(response.text, source)
                parsed_content = f"Title: {title}, Body: {minimized_body}, Links: {link_urls}, Images: {image_urls}"
                compressed_document = [Document(page_content=parsed_content)]
            else:	
                print(f"Failed to retrieve contents from the webpage at url: {source}")

        else:
            loader_kwargs = {}

            if self.node_config is not None:
                loader_kwargs = self.node_config.get("loader_kwargs", {})

            loader = ChromiumLoader([source], headless=self.headless, **loader_kwargs)
            document = loader.load()
            
            title, minimized_body, link_urls, image_urls = cleanup_html(str(document[0].page_content), source)
            parsed_content = f"Title: {title}, Body: {minimized_body}, Links: {link_urls}, Images: {image_urls}"
            
            compressed_document = [
                Document(page_content=parsed_content, metadata={"source": source})
            ]

        state.update({self.output[0]: compressed_document, self.output[1]: link_urls, self.output[2]: image_urls})
        return state