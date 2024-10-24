"""
fetch_node_level_k module
"""
from typing import List, Optional
from urllib.parse import urljoin
from langchain_core.documents import Document
from bs4 import BeautifulSoup
from .base_node import BaseNode
from ..docloaders import ChromiumLoader

class FetchNodeLevelK(BaseNode):
    """
    A node responsible for fetching the HTML content of a specified URL and all its sub-links 
    recursively up to a certain level of hyperlink the graph. This content is then used to update
    the graph's state. It uses ChromiumLoader to fetch the content from a web page asynchronously
    (with proxy protection).

    Attributes:
        embedder_model: An optional model for embedding the fetched content.
        verbose (bool): A flag indicating whether to show print statements during execution.
        cache_path (str): Path to cache fetched content.
        headless (bool): Whether to run the Chromium browser in headless mode.
        loader_kwargs (dict): Additional arguments for the content loader.
        browser_base (dict): Optional configuration for the browser base API.
        depth (int): Maximum depth of hyperlink graph traversal.
        only_inside_links (bool): Whether to fetch only internal links.
        min_input_len (int): Minimum required length of input data.

    Args:
        input (str): Boolean expression defining the input keys needed from the state.
        output (List[str]): List of output keys to be updated in the state.
        node_config (dict): Additional configuration for the node.
        node_name (str): The unique identifier name for the node, defaulting to "FetchLevelK".
    """

    def __init__(
        self,
        input: str,
        output: List[str],
        node_config: Optional[dict] = None,
        node_name: str = "FetchLevelK",
    ):
        """
        Initializes the FetchNodeLevelK instance.

        Args:
            input (str): Boolean expression defining the input keys needed from the state.
            output (List[str]): List of output keys to be updated in the state.
            node_config (Optional[dict]): Additional configuration for the node.
            node_name (str): The name of the node (default is "FetchLevelK").
        """
        super().__init__(node_name, "node", input, output, 2, node_config)

        self.embedder_model = node_config.get("embedder_model", None)
        self.verbose = node_config.get("verbose", False) if node_config else False
        self.cache_path = node_config.get("cache_path", False)
        self.headless = node_config.get("headless", True) if node_config else True
        self.loader_kwargs = node_config.get("loader_kwargs", {}) if node_config else {}
        self.browser_base = node_config.get("browser_base", None)
        self.scrape_do = node_config.get("scrape_do", None)
        self.depth = node_config.get("depth", 1) if node_config else 1
        self.only_inside_links = node_config.get("only_inside_links", False) if node_config else False
        self.min_input_len = 1

    def execute(self, state: dict) -> dict:
        """
        Executes the node's logic to fetch the HTML content of a specified URL and its sub-links
        recursively, then updates the graph's state with the fetched content.

        Args:
            state (dict): The current state of the graph.

        Returns:
            dict: The updated state with a new output key containing the fetched HTML content.

        Raises:
            KeyError: If the input key is not found in the state.
        """
        self.logger.info(f"--- Executing {self.node_name} Node ---")

        input_keys = self.get_input_keys(state)
        input_data = [state[key] for key in input_keys]
        source = input_data[0]

        documents = [{"source": source}]
        loader_kwargs = self.node_config.get("loader_kwargs", {}) if self.node_config else {}

        for _ in range(self.depth):
            documents = self.obtain_content(documents, loader_kwargs)

        filtered_documents = [doc for doc in documents if 'document' in doc]
        state.update({self.output[0]: filtered_documents})
        return state

    def fetch_content(self, source: str, loader_kwargs) -> Optional[str]:
        """
        Fetches the HTML content of a given source URL.

        Args:
            source (str): The URL to fetch content from.
            loader_kwargs (dict): Additional arguments for the content loader.

        Returns:
            Optional[str]: The fetched HTML content or None if fetching failed.
        """
        self.logger.info(f"--- (Fetching HTML from: {source}) ---")

        if self.browser_base is not None:
            try:
                from ..docloaders.browser_base import browser_base_fetch
            except ImportError:
                raise ImportError("""The browserbase module is not installed. 
                                    Please install it using `pip install browserbase`.""")

            data = browser_base_fetch(self.browser_base.get("api_key"),
                                      self.browser_base.get("project_id"), [source])
            document = [Document(page_content=content,
                                 metadata={"source": source}) for content in data]
        elif self.scrape_do:
            from ..docloaders.scrape_do import scrape_do_fetch
            data = scrape_do_fetch(self.scrape_do.get("api_key"), source)
            document = [Document(page_content=data,
                                 metadata={"source": source})]
        else:
            loader = ChromiumLoader([source], headless=self.headless, **loader_kwargs)
            document = loader.load()
        return document

    def extract_links(self, html_content: str) -> list:
        """
        Extracts all hyperlinks from the HTML content.

        Args:
            html_content (str): The HTML content to extract links from.

        Returns:
            list: A list of extracted hyperlinks.
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        links = [link['href'] for link in soup.find_all('a', href=True)]
        self.logger.info(f"Extracted {len(links)} links.")
        return links

    def get_full_links(self, base_url: str, links: list) -> list:
        """
        Converts relative URLs to full URLs based on the base URL.

        Args:
            base_url (str): The base URL for resolving relative links.
            links (list): A list of links to convert.

        Returns:
            list: A list of full URLs.
        """
        full_links = []
        for link in links:
            if self.only_inside_links and link.startswith("http"):
                continue
            full_link = link if link.startswith("http") else urljoin(base_url, link)
            full_links.append(full_link)
        return full_links

    def obtain_content(self, documents: List, loader_kwargs) -> List:
        """
        Iterates through documents, fetching and updating content recursively.

        Args:
            documents (List): A list of documents containing the source URLs.
            loader_kwargs (dict): Additional arguments for the content loader.

        Returns:
            List: The updated list of documents with fetched content.
        """
        new_documents = []
        for doc in documents:
            source = doc['source']
            if 'document' not in doc:
                document = self.fetch_content(source, loader_kwargs)

                if not document or not document[0].page_content.strip():
                    self.logger.warning(f"Failed to fetch content for {source}")
                    documents.remove(doc)
                    continue

                doc['document'] = document
                links = self.extract_links(doc['document'][0].page_content)
                full_links = self.get_full_links(source, links)

                for link in full_links:
                    if not any(d.get('source', '') == link for d in documents) \
                        and not any(d.get('source', '') == link for d in new_documents):
                        new_documents.append({"source": link})

        documents.extend(new_documents)
        return documents

    def process_links(self, base_url: str, links: list, 
                      loader_kwargs, depth: int, current_depth: int = 1) -> dict:
        """
        Processes a list of links recursively up to a given depth.

        Args:
            base_url (str): The base URL for resolving relative links.
            links (list): A list of links to process.
            loader_kwargs (dict): Additional arguments for the content loader.
            depth (int): The maximum depth for recursion.
            current_depth (int): The current depth of recursion (default is 1).

        Returns:
            dict: A dictionary containing processed link content.
        """
        content_dict = {}
        for idx, link in enumerate(links, start=1):
            full_link = link if link.startswith("http") else urljoin(base_url, link)
            self.logger.info(f"Processing link {idx}: {full_link}")
            link_content = self.fetch_content(full_link, loader_kwargs)

            if current_depth < depth:
                new_links = self.extract_links(link_content)
                content_dict.update(self.process_links(full_link, new_links,
                                                       loader_kwargs, depth, current_depth + 1))
            else:
                self.logger.warning(f"Failed to fetch content for {full_link}")
        return content_dict
