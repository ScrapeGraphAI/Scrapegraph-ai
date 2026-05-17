"""
SmartScraperMultiBatchGraph Module

A scraping pipeline that uses the OpenAI Batch API for LLM calls,
providing 50% cost savings compared to real-time API calls.
"""

import asyncio
from copy import deepcopy
from typing import Dict, List, Optional, Type

from pydantic import BaseModel

from ..nodes import FetchNode, GraphIteratorNode, ParseNode
from ..nodes.batch_generate_answer_node import BatchGenerateAnswerNode
from ..nodes.merge_answers_node import MergeAnswersNode
from ..utils.copy import safe_deepcopy
from .abstract_graph import AbstractGraph
from .base_graph import BaseGraph
from .smart_scraper_graph import SmartScraperGraph


class _FetchParseOnlyGraph(AbstractGraph):
    """Internal graph that only fetches and parses a URL (no LLM generation).

    This is used to separate the fetch/parse phase from the LLM generation
    phase, allowing all LLM calls to be batched together.
    """

    def __init__(
        self,
        prompt: str,
        source: str,
        config: dict,
        schema: Optional[Type[BaseModel]] = None,
    ):
        super().__init__(prompt, config, source, schema)
        self.input_key = "url" if source.startswith("http") else "local_dir"

    def _create_graph(self) -> BaseGraph:
        fetch_node = FetchNode(
            input="url | local_dir",
            output=["doc"],
            node_config={
                "llm_model": self.llm_model,
                "force": self.config.get("force", False),
                "cut": self.config.get("cut", True),
                "loader_kwargs": self.config.get("loader_kwargs", {}),
                "browser_base": self.config.get("browser_base"),
                "scrape_do": self.config.get("scrape_do"),
                "storage_state": self.config.get("storage_state"),
            },
        )
        parse_node = ParseNode(
            input="doc",
            output=["parsed_doc"],
            node_config={
                "llm_model": self.llm_model,
                "chunk_size": self.model_token,
            },
        )

        return BaseGraph(
            nodes=[fetch_node, parse_node],
            edges=[(fetch_node, parse_node)],
            entry_point=fetch_node,
            graph_name=self.__class__.__name__,
        )

    def run(self) -> str:
        inputs = {"user_prompt": self.prompt, self.input_key: self.source}
        self.final_state, self.execution_info = self.graph.execute(inputs)
        return self.final_state.get("parsed_doc", "")


class SmartScraperMultiBatchGraph(AbstractGraph):
    """A scraping pipeline that uses OpenAI Batch API for cost savings.

    Similar to SmartScraperMultiGraph, but instead of making individual
    LLM calls per URL, it:
    1. Fetches and parses all URLs concurrently (Phase 1)
    2. Collects all prompts and submits them as a single OpenAI Batch (Phase 2)
    3. Polls for batch completion (Phase 3)
    4. Merges all results into a final answer (Phase 4)

    This provides ~50% cost savings on OpenAI API calls at the expense
    of higher latency (up to 24 hours for batch completion).

    Attributes:
        prompt (str): The user prompt for scraping.
        source (List[str]): List of URLs to scrape.
        config (dict): Configuration including 'llm' and optional 'batch_api' settings.
        schema (Optional[BaseModel]): Optional Pydantic schema for structured output.

    Config options under 'batch_api':
        poll_interval (int): Seconds between batch status checks (default: 30).
        max_wait_time (int): Maximum wait time in seconds (default: 86400 = 24h).
        model (str): Override model for batch requests (optional).
        temperature (float): Temperature for batch requests (default: 0.0).

    Example:
        >>> graph = SmartScraperMultiBatchGraph(
        ...     prompt="Extract the main topic and key points",
        ...     source=[
        ...         "https://example.com/page1",
        ...         "https://example.com/page2",
        ...     ],
        ...     config={
        ...         "llm": {"model": "openai/gpt-4o-mini"},
        ...         "batch_api": {
        ...             "poll_interval": 30,
        ...             "max_wait_time": 3600,
        ...         },
        ...     }
        ... )
        >>> result = graph.run()
    """

    def __init__(
        self,
        prompt: str,
        source: List[str],
        config: dict,
        schema: Optional[Type[BaseModel]] = None,
    ):
        self.copy_config = safe_deepcopy(config)
        self.copy_schema = deepcopy(schema)
        self.batch_config = config.get("batch_api", {})

        # Validate that the model is OpenAI-based
        model_str = config.get("llm", {}).get("model", "")
        if "/" in model_str:
            provider = model_str.split("/")[0]
        else:
            provider = ""
        if provider and provider != "openai":
            raise ValueError(
                f"SmartScraperMultiBatchGraph only supports OpenAI models. "
                f"Got provider '{provider}'. "
                f"Use SmartScraperMultiGraph for other providers."
            )

        super().__init__(prompt, config, source, schema)

    def _create_graph(self) -> BaseGraph:
        """Creates the graph of nodes for the batch scraping pipeline.

        The graph has two phases:
        1. GraphIteratorNode runs _FetchParseOnlyGraph per URL (concurrent)
        2. BatchGenerateAnswerNode submits all prompts via Batch API
        3. MergeAnswersNode combines the results

        Returns:
            BaseGraph: A graph instance representing the batch scraping workflow.
        """
        # Phase 1: Fetch and parse all URLs concurrently
        graph_iterator_node = GraphIteratorNode(
            input="user_prompt & urls",
            output=["parsed_docs"],
            node_config={
                "graph_instance": _FetchParseOnlyGraph,
                "scraper_config": self.copy_config,
            },
            schema=self.copy_schema,
        )

        # Phase 2: Submit all prompts to OpenAI Batch API
        batch_generate_node = BatchGenerateAnswerNode(
            input="user_prompt & parsed_docs",
            output=["results"],
            node_config={
                "llm_model": self.llm_model,
                "schema": self.copy_schema,
                "batch_config": self.batch_config,
            },
        )

        # Phase 3: Merge all results
        merge_answers_node = MergeAnswersNode(
            input="user_prompt & results",
            output=["answer"],
            node_config={
                "llm_model": self.llm_model,
                "schema": self.copy_schema,
            },
        )

        return BaseGraph(
            nodes=[
                graph_iterator_node,
                batch_generate_node,
                merge_answers_node,
            ],
            edges=[
                (graph_iterator_node, batch_generate_node),
                (batch_generate_node, merge_answers_node),
            ],
            entry_point=graph_iterator_node,
            graph_name=self.__class__.__name__,
        )

    def run(self) -> str:
        """Executes the full batch scraping pipeline.

        This will:
        1. Fetch and parse all URLs concurrently
        2. Submit all LLM prompts as an OpenAI Batch
        3. Poll until the batch completes (may take minutes to hours)
        4. Merge results into a final answer

        Returns:
            str: The merged answer from all scraped URLs.
        """
        inputs = {"user_prompt": self.prompt, "urls": self.source}
        self.final_state, self.execution_info = self.graph.execute(inputs)
        return self.final_state.get("answer", "No answer found.")
