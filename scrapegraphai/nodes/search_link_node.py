"""
SearchLinkNode Module
"""
from typing import List, Optional
import re
from tqdm import tqdm
from urllib.parse import urlparse, parse_qs
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableParallel
from ..utils.logging import get_logger
from .base_node import BaseNode
from ..prompts import TEMPLATE_RELEVANT_LINKS
from ..helpers import default_filters


class SearchLinkNode(BaseNode):
    """
    A node that can filter out the relevant links in the webpage content for the user prompt.
    Node expects the already scrapped links on the webpage and hence it is expected
    that this node be used after the FetchNode.

    Attributes:
        llm_model: An instance of the language model client used for generating answers.
        verbose (bool): A flag indicating whether to show print statements during execution.

    Args:
        input (str): Boolean expression defining the input keys needed from the state.
        output (List[str]): List of output keys to be updated in the state.
        node_config (dict): Additional configuration for the node.
        node_name (str): The unique identifier name for the node, defaulting to "GenerateAnswer".
    """

    def __init__(
        self,
        input: str,
        output: List[str],
        node_config: Optional[dict] = None,
        node_name: str = "GenerateLinks",
    ):
        super().__init__(node_name, "node", input, output, 1, node_config)

        self.llm_model = node_config["llm_model"]

        # Apply filters if filter_links is True or if filter_config is provided
        if node_config.get("filter_links", False) or "filter_config" in node_config:
            # Merge provided filter config with default filter config for partial configuration
            provided_filter_config = node_config.get("filter_config", {})
            self.filter_config = {**default_filters.filter_dict, **provided_filter_config}
            self.filter_links = True
        else:
            self.filter_config = None
            self.filter_links = False

        self.verbose = node_config.get("verbose", False)
        self.seen_links = set()

    def _is_same_domain(self, url, domain):
        if not self.filter_links or not self.filter_config.get("diff_domain_filter", True):
            return True
        parsed_url = urlparse(url)
        parsed_domain = urlparse(domain)
        return parsed_url.netloc == parsed_domain.netloc

    def _is_image_url(self, url):
        if not self.filter_links:
            return False
        image_extensions = self.filter_config.get("img_exts", [])
        return any(url.lower().endswith(ext) for ext in image_extensions)

    def _is_language_url(self, url):
        if not self.filter_links:
            return False

        lang_indicators = self.filter_config.get("lang_indicators", [])
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)

        return any(indicator in parsed_url.path.lower() or indicator in query_params for indicator in lang_indicators)
    def _is_potentially_irrelevant(self, url):
        if not self.filter_links:
            return False  # Skip irrelevant URL filtering if filtering is not enabled

        irrelevant_keywords = self.filter_config.get("irrelevant_keywords", [])
        return any(keyword in url.lower() for keyword in irrelevant_keywords)


    def execute(self, state: dict) -> dict:
        """
        Filter out relevant links from the webpage that are relavant to prompt. 
        Out of the filtered links, also ensure that all links are navigable.
        Args:
            state (dict): The current state of the graph. The input keys will be used to fetch the
                            correct data types from the state.

        Returns:
            dict: The updated state with the output key containing the list of links.

        Raises:
            KeyError: If the input keys are not found in the state, indicating that the
                        necessary information for generating the answer is missing.
        """

        self.logger.info(f"--- Executing {self.node_name} Node ---")

        parsed_content_chunks = state.get("doc")
        source_url = state.get("url") or state.get("local_dir")
        output_parser = JsonOutputParser()

        relevant_links = []

        for i, chunk in enumerate(
            tqdm(
                parsed_content_chunks,
                desc="Processing chunks",
                disable=not self.verbose,
            )
        ):
            try:

                # Primary approach: Regular expression to extract links
                links = re.findall(r'https?://[^\s"<>\]]+', str(chunk.page_content))

                if not self.filter_links:
                    links = list(set(links))

                    relevant_links += links
                    self.seen_links.update(relevant_links)
                else:
                    filtered_links = [
                    link for link in links
                    if self._is_same_domain(link, source_url)
                    and not self._is_image_url(link)
                    and not self._is_language_url(link)
                    and not self._is_potentially_irrelevant(link)
                    and link not in self.seen_links
                    ]
                    filtered_links = list(set(filtered_links))
                    relevant_links += filtered_links
                    self.seen_links.update(relevant_links)

            except Exception as e:
                # Fallback approach: Using the LLM to extract links
                self.logger.error(f"Error extracting links: {e}. Falling back to LLM.")

                merge_prompt = PromptTemplate(
                    template=TEMPLATE_RELEVANT_LINKS,
                    input_variables=["content", "user_prompt"],
                )
                merge_chain = merge_prompt | self.llm_model | output_parser
                answer = merge_chain.invoke(
                    {"content": chunk.page_content}
                )
                relevant_links += answer

        state.update({self.output[0]: relevant_links})
        return state
