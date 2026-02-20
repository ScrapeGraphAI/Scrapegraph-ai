"""
BatchGenerateAnswerNode Module

A node that collects LLM prompts from multiple scraped documents
and submits them as a single OpenAI Batch API request for 50% cost savings.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from ..prompts import (
    TEMPLATE_NO_CHUNKS_MD,
    TEMPLATE_NO_CHUNKS,
)
from ..utils.batch_api import (
    BatchRequest,
    BatchResult,
    create_batch,
    poll_batch_until_complete,
    retrieve_batch_results,
)
from ..utils.output_parser import get_pydantic_output_parser
from .base_node import BaseNode

logger = logging.getLogger(__name__)


class BatchGenerateAnswerNode(BaseNode):
    """A node that generates answers using the OpenAI Batch API.

    Instead of making individual LLM calls for each document,
    this node collects all prompts and submits them as a single
    batch request for 50% cost savings.

    Attributes:
        llm_model: The language model configuration (must be OpenAI).
        verbose (bool): Whether to show progress information.

    Args:
        input (str): Boolean expression defining the input keys needed.
        output (List[str]): List of output keys to be updated in the state.
        node_config (Optional[dict]): Configuration dictionary containing:
            - llm_model: The LLM model configuration.
            - schema: Optional Pydantic schema for structured output.
            - additional_info: Optional additional prompt context.
            - batch_config: Optional dict with batch-specific settings:
                - poll_interval: Seconds between status checks (default: 30).
                - max_wait_time: Maximum wait in seconds (default: 86400).
                - model: Override model for batch (optional).
                - temperature: Override temperature (default: 0.0).
        node_name (str): The unique identifier for this node.
    """

    def __init__(
        self,
        input: str,
        output: List[str],
        node_config: Optional[dict] = None,
        node_name: str = "BatchGenerateAnswer",
    ):
        super().__init__(node_name, "node", input, output, 2, node_config)

        self.llm_model = node_config["llm_model"]
        self.verbose = node_config.get("verbose", False)
        self.additional_info = node_config.get("additional_info")
        self.is_md_scraper = node_config.get("is_md_scraper", True)
        self.schema = node_config.get("schema")

        # Batch-specific configuration
        batch_config = node_config.get("batch_config", {})
        self.poll_interval = batch_config.get("poll_interval", 30)
        self.max_wait_time = batch_config.get("max_wait_time", 86_400)
        self.batch_model = batch_config.get("model")
        self.batch_temperature = batch_config.get("temperature", 0.0)

    def _get_model_name(self) -> str:
        """Extract the OpenAI model name from the LLM configuration.

        Returns:
            The model name string (e.g., 'gpt-4o-mini').
        """
        if self.batch_model:
            return self.batch_model

        # Try to extract model name from the LangChain model instance
        if hasattr(self.llm_model, "model_name"):
            return self.llm_model.model_name
        if hasattr(self.llm_model, "model"):
            return self.llm_model.model

        raise ValueError(
            "Could not determine model name from llm_model. "
            "Please specify 'model' in batch_config."
        )

    def _get_format_instructions(self) -> str:
        """Get format instructions based on the schema configuration."""
        if self.schema is not None:
            output_parser = get_pydantic_output_parser(self.schema)
            return output_parser.get_format_instructions()
        return (
            "You must respond with a JSON object. Your response should be "
            "formatted as a valid JSON with a 'content' field containing "
            'your analysis. For example:\n'
            '{"content": "your analysis here"}'
        )

    def _build_prompt_text(
        self,
        user_prompt: str,
        content: str,
        format_instructions: str,
    ) -> str:
        """Build the full prompt text for a single document.

        Args:
            user_prompt: The user's question/prompt.
            content: The scraped document content.
            format_instructions: JSON output format instructions.

        Returns:
            The formatted prompt string.
        """
        template = (
            TEMPLATE_NO_CHUNKS_MD
            if self.is_md_scraper
            else TEMPLATE_NO_CHUNKS
        )

        if self.additional_info:
            template = self.additional_info + template

        prompt = PromptTemplate(
            template=template,
            input_variables=["content", "question"],
            partial_variables={"format_instructions": format_instructions},
        )
        return prompt.format(content=content, question=user_prompt)

    def execute(self, state: dict) -> dict:
        """Execute the batch generation node.

        Takes multiple parsed documents and a user prompt, builds prompts
        for each document, and submits them as a single OpenAI Batch API
        request.

        Args:
            state (dict): Must contain:
                - user_prompt: The user's question.
                - parsed_docs: List of parsed document contents.
                - urls: List of source URLs (for result mapping).

        Returns:
            dict: Updated state with 'results' key containing
                  a list of answers (one per document).
        """
        self.logger.info(f"--- Executing {self.node_name} Node ---")

        user_prompt = state.get("user_prompt", "")
        parsed_docs = state.get("parsed_docs", [])
        urls = state.get("urls", [])

        if not parsed_docs:
            raise ValueError("No parsed documents found in state")

        model_name = self._get_model_name()
        format_instructions = self._get_format_instructions()

        # Build batch requests with doc_id → URL mapping
        batch_requests = []
        doc_id_to_url = {}

        for i, doc in enumerate(parsed_docs):
            custom_id = f"doc_{i:04d}"
            doc_id_to_url[custom_id] = urls[i] if i < len(urls) else f"doc_{i}"

            # Handle chunked documents — use first chunk for batch
            content = doc[0] if isinstance(doc, list) and len(doc) == 1 else str(doc)

            prompt_text = self._build_prompt_text(
                user_prompt, content, format_instructions
            )

            batch_requests.append(BatchRequest(
                custom_id=custom_id,
                model=model_name,
                messages=[{"role": "user", "content": prompt_text}],
                temperature=self.batch_temperature,
                response_format={"type": "json_object"},
            ))

        self.logger.info(
            f"Submitting {len(batch_requests)} requests to "
            f"OpenAI Batch API (model: {model_name})..."
        )

        # Submit batch
        from openai import OpenAI

        client = OpenAI()
        batch_id = create_batch(
            client,
            batch_requests,
            description=f"ScrapeGraphAI: {user_prompt[:100]}",
        )

        self.logger.info(f"Batch submitted: {batch_id}")
        state["batch_id"] = batch_id

        # Poll until complete
        batch_info = poll_batch_until_complete(
            client,
            batch_id,
            poll_interval=self.poll_interval,
            max_wait_time=self.max_wait_time,
        )

        # Retrieve results
        results = retrieve_batch_results(client, batch_info)

        # Parse results back into answers, maintaining URL order
        answers = []
        for result in results:
            if result.error:
                self.logger.warning(
                    f"Request {result.custom_id} "
                    f"(URL: {doc_id_to_url.get(result.custom_id, 'unknown')}) "
                    f"failed: {result.error}"
                )
                answers.append({"error": result.error})
                continue

            try:
                parsed = json.loads(result.content)
                answers.append(parsed)
            except (json.JSONDecodeError, TypeError):
                # If not valid JSON, wrap the raw content
                answers.append({"content": result.content})

        self.logger.info(
            f"Batch complete: {len(answers)} answers retrieved "
            f"({sum(1 for a in answers if 'error' not in a)} succeeded)"
        )

        state.update({
            self.output[0]: answers,
            "doc_id_to_url": doc_id_to_url,
        })
        return state
