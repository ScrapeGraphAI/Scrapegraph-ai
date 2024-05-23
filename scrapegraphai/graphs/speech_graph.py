""" 
SpeechGraph Module
"""

from typing import Optional

from .base_graph import BaseGraph
from .abstract_graph import AbstractGraph

from ..nodes import (
    FetchNode,
    ParseNode,
    RAGNode,
    GenerateAnswerNode,
    TextToSpeechNode,
)

from ..utils.save_audio_from_bytes import save_audio_from_bytes
from ..models import OpenAITextToSpeech


class SpeechGraph(AbstractGraph):
    """
    SpeechyGraph is a scraping pipeline that scrapes the web, provide an answer to a given prompt, and generate an audio file.

    Attributes:
        prompt (str): The prompt for the graph.
        source (str): The source of the graph.
        config (dict): Configuration parameters for the graph.
        schema (str): The schema for the graph output.
        llm_model: An instance of a language model client, configured for generating answers.
        embedder_model: An instance of an embedding model client, configured for generating embeddings.
        verbose (bool): A flag indicating whether to show print statements during execution.
        headless (bool): A flag indicating whether to run the graph in headless mode.
        model_token (int): The token limit for the language model.

    Args:
        prompt (str): The prompt for the graph.
        source (str): The source of the graph.
        config (dict): Configuration parameters for the graph.
        schema (str): The schema for the graph output.

    Example:
        >>> speech_graph = SpeechGraph(
        ...     "List me all the attractions in Chioggia and generate an audio summary.",
        ...     "https://en.wikipedia.org/wiki/Chioggia",
        ...     {"llm": {"model": "gpt-3.5-turbo"}}
    """

    def __init__(self, prompt: str, source: str, config: dict, schema: Optional[str] = None):
        super().__init__(prompt, config, source, schema)

        self.input_key = "url" if source.startswith("http") else "local_dir"

    def _create_graph(self) -> BaseGraph:
        """
        Creates the graph of nodes representing the workflow for web scraping and audio generation.

        Returns:
            BaseGraph: A graph instance representing the web scraping and audio generation workflow.
        """

        fetch_node = FetchNode(
            input="url | local_dir",
            output=["doc", "link_urls", "img_urls"]
        )
        parse_node = ParseNode(
            input="doc",
            output=["parsed_doc"],
            node_config={
                "chunk_size": self.model_token
            }
        )
        rag_node = RAGNode(
            input="user_prompt & (parsed_doc | doc)",
            output=["relevant_chunks"],
            node_config={
                "llm_model": self.llm_model,
                "embedder_model": self.embedder_model            }
        )
        generate_answer_node = GenerateAnswerNode(
            input="user_prompt & (relevant_chunks | parsed_doc | doc)",
            output=["answer"],
            node_config={
                "llm_model": self.llm_model,
                "schema": self.schema
            }
        )
        text_to_speech_node = TextToSpeechNode(
            input="answer",
            output=["audio"],
            node_config={
                "tts_model": OpenAITextToSpeech(self.config["tts_model"])
            }
        )

        return BaseGraph(
            nodes=[
                fetch_node,
                parse_node,
                rag_node,
                generate_answer_node,
                text_to_speech_node
            ],
            edges=[
                (fetch_node, parse_node),
                (parse_node, rag_node),
                (rag_node, generate_answer_node),
                (generate_answer_node, text_to_speech_node)
            ],
            entry_point=fetch_node
        )

    def run(self) -> str:
        """
        Executes the scraping process and returns the answer to the prompt.

        Returns:
            str: The answer to the prompt.
        """
        
        inputs = {"user_prompt": self.prompt, self.input_key: self.source}
        self.final_state, self.execution_info = self.graph.execute(inputs)

        audio = self.final_state.get("audio", None)
        if not audio:
            raise ValueError("No audio generated from the text.")
        save_audio_from_bytes(audio, self.config.get(
            "output_path", "output.mp3"))
        print(f"Audio saved to {self.config.get('output_path', 'output.mp3')}")

        return self.final_state.get("answer", "No answer found.")