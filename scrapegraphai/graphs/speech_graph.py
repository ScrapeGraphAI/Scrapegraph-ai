""" 
Module for converting text to speach
"""
from scrapegraphai.utils.save_audio_from_bytes import save_audio_from_bytes
from ..models import OpenAI, Gemini, OpenAITextToSpeech
from .base_graph import BaseGraph
from ..nodes import (
    FetchNode,
    ParseNode,
    RAGNode,
    GenerateAnswerNode,
    TextToSpeechNode,
)
from .abstract_graph import AbstractGraph


class SpeechGraph(AbstractGraph):
    """
    SpeechSummaryGraph is a tool that automates the process of extracting and summarizing
    information from web pages, then converting that summary into spoken word via an MP3 file.
    """

    def _create_graph(self):
        """
        Creates the graph of nodes representing the workflow for web scraping and summarization.
        """
        fetch_node = FetchNode(
            input="url | local_dir",
            output=["doc"],
        )
        parse_node = ParseNode(
            input="doc",
            output=["parsed_doc"],
        )
        rag_node = RAGNode(
            input="user_prompt & (parsed_doc | doc)",
            output=["relevant_chunks"],
            node_config={"llm": self.llm_model},
        )
        generate_answer_node = GenerateAnswerNode(
            input="user_prompt & (relevant_chunks | parsed_doc | doc)",
            output=["answer"],
            node_config={"llm": self.llm_model},
        )
        text_to_speech_node = TextToSpeechNode(
            input="answer",
            output=["audio"],
            node_config={"tts_model": OpenAITextToSpeech(
                self.config["tts_model"])},
        )

        return BaseGraph(
            nodes={
                fetch_node,
                parse_node,
                rag_node,
                generate_answer_node,
                text_to_speech_node
            },
            edges={
                (fetch_node, parse_node),
                (parse_node, rag_node),
                (rag_node, generate_answer_node),
                (generate_answer_node, text_to_speech_node)
            },
            entry_point=fetch_node
        )

    def run(self) -> str:
        """
        Executes the web scraping, summarization, and text-to-speech process.
        """
        inputs = {"user_prompt": self.prompt, self.input_key: self.source}
        final_state = self.graph.execute(inputs)

        audio = final_state.get("audio", None)
        if not audio:
            raise ValueError("No audio generated from the text.")
        save_audio_from_bytes(audio, self.config.get(
            "output_path", "output.mp3"))
        print(f"Audio saved to {self.config.get('output_path', 'output.mp3')}")

        return final_state
