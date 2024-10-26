"""
SmartScraperGraph Module
"""
from typing import Optional
from pydantic import BaseModel
from .base_graph import BaseGraph
from .abstract_graph import AbstractGraph
from ..nodes import (
    FetchNode,
    ParseNode,
    ReasoningNode,
    GenerateAnswerNode,
    ConditionalNode
)
from ..prompts import REGEN_ADDITIONAL_INFO

class SmartScraperGraph(AbstractGraph):
    """
    SmartScraper is a scraping pipeline that automates the process of 
    extracting information from web pages
    using a natural language model to interpret and answer prompts.

    Attributes:
        prompt (str): The prompt for the graph.
        source (str): The source of the graph.
        config (dict): Configuration parameters for the graph.
        schema (BaseModel): The schema for the graph output.
        llm_model: An instance of a language model client, configured for generating answers.
        embedder_model: An instance of an embedding model client, 
        configured for generating embeddings.
        verbose (bool): A flag indicating whether to show print statements during execution.
        headless (bool): A flag indicating whether to run the graph in headless mode.

    Args:
        prompt (str): The prompt for the graph.
        source (str): The source of the graph.
        config (dict): Configuration parameters for the graph.
        schema (BaseModel): The schema for the graph output.

    Example:
        >>> smart_scraper = SmartScraperGraph(
        ...     "List me all the attractions in Chioggia.",
        ...     "https://en.wikipedia.org/wiki/Chioggia",
        ...     {"llm": {"model": "openai/gpt-3.5-turbo"}}
        ... )
        >>> result = smart_scraper.run()
        )
    """

    def __init__(self, prompt: str, source: str, config: dict, schema: Optional[BaseModel] = None):
        super().__init__(prompt, config, source, schema)

        self.input_key = "url" if source.startswith("http") else "local_dir"

    def _create_graph(self) -> BaseGraph:
        """
        Creates the graph of nodes representing the workflow for web scraping.

        Returns:
            BaseGraph: A graph instance representing the web scraping workflow.
        """

        fetch_node = FetchNode(
            input="url| local_dir",
            output=["doc"],
            node_config={
                "llm_model": self.llm_model,
                "force": self.config.get("force", False),
                "cut": self.config.get("cut", True),
                "loader_kwargs": self.config.get("loader_kwargs", {}),
                "browser_base": self.config.get("browser_base"),
                "scrape_do": self.config.get("scrape_do")
            }
        )
        parse_node = ParseNode(
            input="doc",
            output=["parsed_doc"],
            node_config={
                "llm_model": self.llm_model,
                "chunk_size": self.model_token
            }
        )

        generate_answer_node = GenerateAnswerNode(
            input="user_prompt & (relevant_chunks | parsed_doc | doc)",
            output=["answer"],
            node_config={
                "llm_model": self.llm_model,
                "additional_info": self.config.get("additional_info"),
                "schema": self.schema,
            }
        )

        cond_node = None
        regen_node = None
        if self.config.get("reattempt") is True:
            cond_node = ConditionalNode(
                input="answer",
                output=["answer"],
                node_name="ConditionalNode",
                node_config={
                    "key_name": "answer",
                    "condition": 'not answer or answer=="NA"',
                }
            )
            regen_node = GenerateAnswerNode(
                input="user_prompt & answer",
                output=["answer"],
                node_config={
                    "llm_model": self.llm_model,
                    "additional_info": REGEN_ADDITIONAL_INFO,
                    "schema": self.schema,
                }
            )

        if self.config.get("html_mode") is False:
            parse_node = ParseNode(
                input="doc",
                output=["parsed_doc"],
                node_config={
                    "llm_model": self.llm_model,
                    "chunk_size": self.model_token
                }
            )

        reasoning_node = None
        if self.config.get("reasoning"):
            reasoning_node =  ReasoningNode(
                input="user_prompt & (relevant_chunks | parsed_doc | doc)",
                output=["answer"],
                node_config={
                    "llm_model": self.llm_model,
                    "additional_info": self.config.get("additional_info"),
                    "schema": self.schema,
                }
            )
            
        # Define the graph variation configurations
        # (html_mode, reasoning, reattempt)
        graph_variation_config = {
            (False, True, False): {
            "nodes": [fetch_node, parse_node, reasoning_node, generate_answer_node],
            "edges": [(fetch_node, parse_node), (parse_node, reasoning_node), (reasoning_node, generate_answer_node)]
            },
            (True, True, False): {
                "nodes": [fetch_node, reasoning_node, generate_answer_node],
                "edges": [(fetch_node, reasoning_node), (reasoning_node, generate_answer_node)]
            },
            (True, False, False): {
                "nodes": [fetch_node, generate_answer_node],
                "edges": [(fetch_node, generate_answer_node)]
            },
            (False, False, False): {
                "nodes": [fetch_node, parse_node, generate_answer_node],
                "edges": [(fetch_node, parse_node), (parse_node, generate_answer_node)]
            },
            (False, True, True): {
                "nodes": [fetch_node, parse_node, reasoning_node, generate_answer_node, cond_node, regen_node],
                "edges": [(fetch_node, parse_node), (parse_node, reasoning_node), (reasoning_node, generate_answer_node), 
                          (generate_answer_node, cond_node), (cond_node, regen_node), (cond_node, None)]
            },
            (True, True, True): {
                "nodes": [fetch_node, reasoning_node, generate_answer_node, cond_node, regen_node],
                "edges": [(fetch_node, reasoning_node), (reasoning_node, generate_answer_node), 
                          (generate_answer_node, cond_node), (cond_node, regen_node), (cond_node, None)]
            },
            (True, False, True): {
                "nodes": [fetch_node, generate_answer_node, cond_node, regen_node],
                "edges": [(fetch_node, generate_answer_node), (generate_answer_node, cond_node), 
                          (cond_node, regen_node), (cond_node, None)]
            },
            (False, False, True): {
                "nodes": [fetch_node, parse_node, generate_answer_node, cond_node, regen_node],
                "edges": [(fetch_node, parse_node), (parse_node, generate_answer_node), 
                          (generate_answer_node, cond_node), (cond_node, regen_node), (cond_node, None)]
            }
        }

        # Get the current conditions
        html_mode = self.config.get("html_mode", False)
        reasoning = self.config.get("reasoning", False)
        reattempt = self.config.get("reattempt", False)

        # Retrieve the appropriate graph configuration
        config = graph_variation_config.get((html_mode, reasoning, reattempt))

        if config:
            return BaseGraph(
                nodes=config["nodes"],
                edges=config["edges"],
                entry_point=fetch_node,
                graph_name=self.__class__.__name__
            )

        # Default return if no conditions match
        return BaseGraph(
            nodes=[fetch_node, parse_node, generate_answer_node],
            edges=[(fetch_node, parse_node), (parse_node, generate_answer_node)],
            entry_point=fetch_node,
            graph_name=self.__class__.__name__
        )
        
    def run(self) -> str:
        """
        Executes the scraping process and returns the answer to the prompt.

        Returns:
            str: The answer to the prompt.
        """

        inputs = {"user_prompt": self.prompt, self.input_key: self.source}
        self.final_state, self.execution_info = self.graph.execute(inputs)

        return self.final_state.get("answer", "No answer found.")
