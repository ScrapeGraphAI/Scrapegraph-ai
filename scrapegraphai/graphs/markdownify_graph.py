"""
markdownify_graph module
"""

from typing import Dict, List, Optional, Tuple

from ..nodes import (
    FetchNode,
    MarkdownifyNode,
)
from .base_graph import BaseGraph


class MarkdownifyGraph(BaseGraph):
    """
    A graph that converts HTML content to Markdown format.

    This graph takes a URL or HTML content as input and converts it to clean, readable Markdown.
    It uses a two-step process:
    1. Fetch the content (if URL is provided)
    2. Convert the content to Markdown format

    Args:
        llm_model: The language model to use for processing
        embedder_model: The embedding model to use (optional)
        node_config: Additional configuration for the nodes (optional)

    Example:
        >>> graph = MarkdownifyGraph(
        ...     llm_model=your_llm_model,
        ...     embedder_model=your_embedder_model
        ... )
        >>> result, _ = graph.execute({"url": "https://example.com"})
        >>> print(result["markdown"])
    """

    def __init__(
        self,
        llm_model,
        embedder_model=None,
        node_config: Optional[Dict] = None,
    ):
        # Initialize nodes
        fetch_node = FetchNode(
            input="url | html",
            output=["html_content"],
            node_config=node_config,
        )

        markdownify_node = MarkdownifyNode(
            input="html_content",
            output=["markdown"],
            node_config=node_config,
        )

        # Define graph structure
        nodes = [fetch_node, markdownify_node]
        edges = [(fetch_node, markdownify_node)]

        super().__init__(
            nodes=nodes,
            edges=edges,
            entry_point=fetch_node,
            graph_name="Markdownify",
        )

    def execute(self, initial_state: Dict) -> Tuple[Dict, List[Dict]]:
        """
        Execute the markdownify graph.

        Args:
            initial_state: A dictionary containing either:
                - "url": The URL to fetch and convert to markdown
                - "html": The HTML content to convert to markdown

        Returns:
            Tuple containing:
                - Dictionary with the markdown result in the "markdown" key
                - List of execution logs
        """
        return super().execute(initial_state)
