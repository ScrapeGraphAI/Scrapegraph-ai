"""
SmartScraperGraph Module
"""
from typing import Optional
import logging
from pydantic import BaseModel
from .base_graph import BaseGraph
from .abstract_graph import AbstractGraph
from ..utils.save_code_to_file import save_code_to_file
from ..nodes import (
    FetchNode,
    ParseNode,
    GenerateAnswerNode,
    PromptRefinerNode,
    HtmlAnalyzerNode,
    GenerateCodeNode,
)

class CodeGeneratorGraph(AbstractGraph):
    """
    CodeGeneratorGraph is a script generator pipeline that generates 
    the function extract_data(html: str) -> dict() for
    extracting the wanted information from a HTML page. 
    The code generated is in Python and uses the library BeautifulSoup.
    It requires a user prompt, a source URL, and an output schema.

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
        library (str): The library used for web scraping (beautiful soup).

    Args:
        prompt (str): The prompt for the graph.
        source (str): The source of the graph.
        config (dict): Configuration parameters for the graph.
        schema (BaseModel): The schema for the graph output.

    Example:
        >>> code_gen = CodeGeneratorGraph(
        ...     "List me all the attractions in Chioggia.",
        ...     "https://en.wikipedia.org/wiki/Chioggia",
        ...     {"llm": {"model": "openai/gpt-3.5-turbo"}}
        ... )
        >>> result = code_gen.run()
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

        if self.schema is None:
            raise KeyError("The schema is required for CodeGeneratorGraph")

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

        generate_validation_answer_node = GenerateAnswerNode(
            input="user_prompt & (relevant_chunks | parsed_doc | doc)",
            output=["answer"],
            node_config={
                "llm_model": self.llm_model,
                "additional_info": self.config.get("additional_info"),
                "schema": self.schema,
            }
        )

        prompt_refier_node = PromptRefinerNode(
            input="user_prompt",
            output=["refined_prompt"],
            node_config={
                "llm_model": self.llm_model,
                "chunk_size": self.model_token,
                "schema": self.schema
            }
        )

        html_analyzer_node = HtmlAnalyzerNode(
            input="refined_prompt & original_html",
            output=["html_info", "reduced_html"],
            node_config={
                "llm_model": self.llm_model,
                "additional_info": self.config.get("additional_info"),
                "schema": self.schema,
                "reduction": self.config.get("reduction", 0)
            }
        )

        generate_code_node = GenerateCodeNode(
            input="user_prompt & refined_prompt & html_info & reduced_html & answer",
            output=["generated_code"],
            node_config={
                "llm_model": self.llm_model,
                "additional_info": self.config.get("additional_info"),
                "schema": self.schema,
                "max_iterations": self.config.get("max_iterations", {
                    "overall": 10,
                    "syntax": 3,
                    "execution": 3,
                    "validation": 3,
                    "semantic": 3
                }),
            }
        )

        return BaseGraph(
            nodes=[
                fetch_node,
                parse_node,
                generate_validation_answer_node,
                prompt_refier_node,
                html_analyzer_node,
                generate_code_node,
            ],
            edges=[
                (fetch_node, parse_node),
                (parse_node, generate_validation_answer_node),
                (generate_validation_answer_node, prompt_refier_node),
                (prompt_refier_node, html_analyzer_node),
                (html_analyzer_node, generate_code_node)
            ],
            entry_point=fetch_node,
            graph_name=self.__class__.__name__
        )

    def run(self) -> str:
        """
        Executes the scraping process and returns the generated code.

        Returns:
            str: The generated code.
        """

        inputs = {"user_prompt": self.prompt, self.input_key: self.source}
        self.final_state, self.execution_info = self.graph.execute(inputs)

        generated_code = self.final_state.get("generated_code", "No code created.")

        if self.config.get("filename") is None:
            filename = "extracted_data.py"
        elif ".py" not in self.config.get("filename"):
            filename += ".py"
        else:
            filename = self.config.get("filename")

        save_code_to_file(generated_code, filename)

        return generated_code
