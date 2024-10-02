"""
FetchNodeLevelK Module
"""
from typing import List, Optional
from .base_node import BaseNode
from ..docloaders import ChromiumLoader
from ..utils.cleanup_html import cleanup_html
from ..utils.convert_to_md import convert_to_md
from langchain_core.documents import Document
from bs4 import BeautifulSoup
from urllib.parse import quote, urljoin

class FetchNodeLevelK(BaseNode):
    """
    A node responsible for fetching the HTML content of a specified URL and all its sub-links 
    recursively up to a certain level of hyperlink the graph. This content is then used to update
    the graph's state. It uses ChromiumLoader to fetch the content from a web page asynchronously
    (with proxy protection).

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
        node_name: str = "FetchLevelK",
    ):
        super().__init__(node_name, "node", input, output, 2, node_config)
        
        self.embedder_model = node_config.get("embedder_model", None)
        
        self.verbose = (
            False if node_config is None else node_config.get("verbose", False)
        )
        
        self.cache_path = node_config.get("cache_path", False)
        
        self.headless = (
            True if node_config is None else node_config.get("headless", True)
        )
        
        self.loader_kwargs = (
            {} if node_config is None else node_config.get("loader_kwargs", {})
        )
        
        self.browser_base = (
            None if node_config is None else node_config.get("browser_base", None)
        )
        
        self.depth = (
            1 if node_config is None else node_config.get("depth", 1)
        )
        
        self.only_inside_links = (
            False if node_config is None else node_config.get("only_inside_links", False)
        )
        
        self.min_input_len = 1

    def execute(self, state: dict) -> dict:
        """
        Executes the node's logic to fetch the HTML content of a specified URL and all its sub-links
        and update the graph's state with the content.

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
        
        documents = [{"source": source}]
        
        self.logger.info(f"--- (Fetching HTML from: {source}) ---")
        
        loader_kwargs = {}

        if self.node_config is not None:
            loader_kwargs = self.node_config.get("loader_kwargs", {})
        
        for _ in range(self.depth):
            documents = self.obtain_content(documents, loader_kwargs)
        
        filtered_documents = [doc for doc in documents if 'document' in doc]
        
        state.update({self.output[0]: filtered_documents})
        
        return state
    
    def fetch_content(self, source: str, loader_kwargs) -> Optional[str]:
        if self.browser_base is not None:
            try:
                from ..docloaders.browser_base import browser_base_fetch
            except ImportError:
                raise ImportError("""The browserbase module is not installed. 
                                    Please install it using `pip install browserbase`.""")

            data =  browser_base_fetch(self.browser_base.get("api_key"),
                                        self.browser_base.get("project_id"), [source])

            document = [Document(page_content=content,
                                metadata={"source": source}) for content in data]
        
        else:
            loader = ChromiumLoader([source], headless=self.headless, **loader_kwargs)
            
            document = loader.load()
        
        return document
    
    def extract_links(self, html_content: str) -> list:
        soup = BeautifulSoup(html_content, 'html.parser')
        links = [link['href'] for link in soup.find_all('a', href=True)]
        self.logger.info(f"Extracted {len(links)} links.")
        return links
    
    def get_full_links(self, base_url: str, links: list) -> list:
        full_links = []
        for link in links:
            if self.only_inside_links and link.startswith("http"):
                continue
            full_link = link if link.startswith("http") else urljoin(base_url, link)
            full_links.append(full_link)
        return full_links
    
    def obtain_content(self, documents: List, loader_kwargs) -> List:
        new_documents = []
        for doc in documents:
            source = doc['source']
            if 'document' not in doc:
                document = self.fetch_content(source, loader_kwargs)
                
                if not document or not document[0].page_content.strip():
                    self.logger.warning(f"Failed to fetch content for {source}")
                    documents.remove(doc)
                    continue
                
                doc['document'] = document[0].page_content
                
                links = self.extract_links(doc['document'])
                full_links = self.get_full_links(source, links)
                
                # Check if the links are already present in other documents
                for link in full_links:
                    # Check if any document is from the same link
                    if not any(d.get('source', '') == link for d in documents) and not any(d.get('source', '') == link for d in new_documents):
                        # Add the document
                        new_documents.append({"source": link})
        
        documents.extend(new_documents)
        return documents
    
    def process_links(self, base_url: str, links: list, loader_kwargs, depth: int, current_depth: int = 1) -> dict:
        content_dict = {}
        for idx, link in enumerate(links, start=1):
            full_link = link if link.startswith("http") else urljoin(base_url, link)
            self.logger.info(f"Processing link {idx}: {full_link}")
            link_content = self.fetch_content(full_link, loader_kwargs)

            if current_depth < depth:
                new_links = self.extract_links(link_content)
                content_dict.update(self.process_links(full_link, new_links, depth, current_depth + 1))
            else:
                self.logger.warning(f"Failed to fetch content for {full_link}")
        return content_dict