"""
FetchNode Module
"""
import json
from typing import List, Optional
from langchain_openai import ChatOpenAI, AzureChatOpenAI
import pandas as pd
import requests
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from ..utils.cleanup_html import cleanup_html
from ..docloaders import ChromiumLoader
from ..utils.convert_to_md import convert_to_md
from ..utils.logging import get_logger
from .base_node import BaseNode

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
        super().__init__(node_name, "node", input, output, 1, node_config)

        self.headless = (
            True if node_config is None else node_config.get("headless", True)
        )
        self.verbose = (
            False if node_config is None else node_config.get("verbose", False)
        )
        self.use_soup = (
            False if node_config is None else node_config.get("use_soup", False)
        )
        self.loader_kwargs = (
            {} if node_config is None else node_config.get("loader_kwargs", {})
        )
        self.llm_model = (
            {} if node_config is None else node_config.get("llm_model", {})
        )
        self.force = (
            False if node_config is None else node_config.get("force", False)
        )
        self.script_creator = (
            False if node_config is None else node_config.get("script_creator", False)
        )
        self.openai_md_enabled = (
            False if node_config is None else node_config.get("openai_md_enabled", False)
        )

        self.cut = (
            False if node_config is None else node_config.get("cut", True)
        )

        self.browser_base = (
            None if node_config is None else node_config.get("browser_base", None)
        )

        self.scrape_do = (
            None if node_config is None else node_config.get("scrape_do", None)
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

        self.logger.info(f"--- Executing {self.node_name} Node ---")

        # Interpret input keys based on the provided input expression
        input_keys = self.get_input_keys(state)
        # Fetching data from the state based on the input keys
        input_data = [state[key] for key in input_keys]

        source = input_data[0]
        input_type = input_keys[0]

        handlers = {
            "json_dir": self.handle_directory,
            "xml_dir": self.handle_directory,
            "csv_dir": self.handle_directory,
            "pdf_dir": self.handle_directory,
            "md_dir": self.handle_directory,
            "pdf": self.handle_file,
            "csv": self.handle_file,
            "json": self.handle_file,
            "xml": self.handle_file,
            "md": self.handle_file,
        }

        if input_type in handlers:
            return handlers[input_type](state, input_type, source)
        elif self.input == "pdf_dir":
            return state
        elif not source.startswith("http") and not source.startswith("www"):
            return self.handle_local_source(state, source)
        else:
            return self.handle_web_source(state, source)

    def handle_directory(self, state, input_type, source):
        """
        Handles the directory by compressing the source document and updating the state.

        Parameters:
        state (dict): The current state of the graph.
        input_type (str): The type of input being processed.
        source (str): The source document to be compressed.

        Returns:
        dict: The updated state with the compressed document.
        """

        compressed_document = [
            source
        ]
        state.update({self.output[0]: compressed_document})
        return state

    def handle_file(self, state, input_type, source):
        """
        Loads the content of a file based on its input type.

        Parameters:
        state (dict): The current state of the graph.
        input_type (str): The type of the input file (e.g., "pdf", "csv", "json", "xml", "md").
        source (str): The path to the source file.

        Returns:
        dict: The updated state with the compressed document.

        The function supports the following input types:
        - "pdf": Uses PyPDFLoader to load the content of a PDF file.
        - "csv": Reads the content of a CSV file using pandas and converts it to a string.
        - "json": Loads the content of a JSON file.
        - "xml": Reads the content of an XML file as a string.
        - "md": Reads the content of a Markdown file as a string.
        """

        compressed_document = self.load_file_content(source, input_type)

        return self.update_state(state, compressed_document)

    def load_file_content(self, source, input_type):
        """
        Loads the content of a file based on its input type.

        Parameters:
        source (str): The path to the source file.
        input_type (str): The type of the input file (e.g., "pdf", "csv", "json", "xml", "md").

        Returns:
        list: A list containing a Document object with the loaded content and metadata.
        """

        if input_type == "pdf":
            loader = PyPDFLoader(source)
            return loader.load()
        elif input_type == "csv":
            return [Document(page_content=str(pd.read_csv(source)), metadata={"source": "csv"})]
        elif input_type == "json":
            with open(source, encoding="utf-8") as f:
                return [Document(page_content=str(json.load(f)), metadata={"source": "json"})]
        elif input_type == "xml" or input_type == "md":
            with open(source, "r", encoding="utf-8") as f:
                data = f.read()
            return [Document(page_content=data, metadata={"source": input_type})]

    def handle_local_source(self, state, source):
        """
        Handles the local source by fetching HTML content, optionally converting it to Markdown,
        and updating the state.

        Parameters:
        state (dict): The current state of the graph.
        source (str): The HTML content from the local source.

        Returns:
        dict: The updated state with the processed content.

        Raises:
        ValueError: If the source is empty or contains only whitespace.
        """

        self.logger.info(f"--- (Fetching HTML from: {source}) ---")
        if not source.strip():
            raise ValueError("No HTML body content found in the local source.")

        parsed_content = source

        if (isinstance(self.llm_model, ChatOpenAI) or \
            isinstance(self.llm_model, AzureChatOpenAI)) \
                and not self.script_creator or self.force and not self.script_creator:
            parsed_content = convert_to_md(source)
        else:
            parsed_content = source

        compressed_document = [
            Document(page_content=parsed_content, metadata={"source": "local_dir"})
        ]

        return self.update_state(state, compressed_document)

    def handle_web_source(self, state, source):
        """
        Handles the web source by fetching HTML content from a URL, 
        optionally converting it to Markdown, and updating the state.

        Parameters:
        state (dict): The current state of the graph.
        source (str): The URL of the web source to fetch HTML content from.

        Returns:
        dict: The updated state with the processed content.

        Raises:
        ValueError: If the fetched HTML content is empty or contains only whitespace.
        """

        self.logger.info(f"--- (Fetching HTML from: {source}) ---")
        if self.use_soup:
            response = requests.get(source)
            if response.status_code == 200:
                if not response.text.strip():
                    raise ValueError("No HTML body content found in the response.")

                if not self.cut:
                    parsed_content = cleanup_html(response, source)

                if isinstance(self.llm_model, (ChatOpenAI, AzureChatOpenAI)) \
                    and not self.script_creator or (self.force and not self.script_creator):
                    parsed_content = convert_to_md(source, parsed_content)

                compressed_document = [Document(page_content=parsed_content)]
            else:
                self.logger.warning(
                    f"Failed to retrieve contents from the webpage at url: {source}"
                )
        else:
            loader_kwargs = {}

            if self.node_config:
                loader_kwargs = self.node_config.get("loader_kwargs", {})

            if self.browser_base:
                try:
                    from ..docloaders.browser_base import browser_base_fetch
                except ImportError:
                    raise ImportError("""The browserbase module is not installed. 
                                      Please install it using `pip install browserbase`.""")

                data =  browser_base_fetch(self.browser_base.get("api_key"),
                                            self.browser_base.get("project_id"), [source])

                document = [Document(page_content=content,
                                    metadata={"source": source}) for content in data]
            elif self.scrape_do:
                from ..docloaders.scrape_do import scrape_do_fetch
                if (self.scrape_do.get("use_proxy") is None) or \
                self.scrape_do.get("geoCode") is None or \
                self.scrape_do.get("super_proxy") is None:
                    data =  scrape_do_fetch(self.scrape_do.get("api_key"),
                                                source)
                else:
                    data =  scrape_do_fetch(self.scrape_do.get("api_key"),
                                                source, self.scrape_do.get("use_proxy"),
                                                self.scrape_do.get("geoCode"),
                                                self.scrape_do.get("super_proxy"))

                document = [Document(page_content=data,
                                    metadata={"source": source})]
            else:
                loader = ChromiumLoader([source], headless=self.headless, **loader_kwargs)
                document = loader.load()

            if not document or not document[0].page_content.strip():
                raise ValueError("""No HTML body content found in
                                 the document fetched by ChromiumLoader.""")

            parsed_content = document[0].page_content

            if (isinstance(self.llm_model, ChatOpenAI) \
                or isinstance(self.llm_model, AzureChatOpenAI)) \
                and not self.script_creator or self.force \
                and not self.script_creator and not self.openai_md_enabled:
                parsed_content = convert_to_md(document[0].page_content, parsed_content)

            compressed_document = [
                Document(page_content=parsed_content, metadata={"source": "html file"})
            ]
        state["original_html"] = document
        state.update({self.output[0]: compressed_document,})
        return state
