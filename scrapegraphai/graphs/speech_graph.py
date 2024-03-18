""" 
Module for extracting the summary from the speach
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


class SpeechGraph:
    """
    SpeechSummaryGraph is a tool that automates the process of extracting and summarizing
    information from web pages, then converting that summary into spoken word via an MP3 file.

    Attributes:
        url (str): The URL of the web page to scrape and summarize.
        llm_config (dict): Configuration parameters for the language model, 
        with 'api_key' mandatory.
        summary_prompt (str): The prompt used to guide the summarization process.
        output_path (Path): The path where the generated MP3 file will be saved.

    Methods:
        run(): Executes the web scraping, summarization, and text-to-speech process.

    Args:
        url (str): The URL of the web page to scrape and summarize.
        llm_config (dict): A dictionary containing configuration options for the language model.
        summary_prompt (str): The prompt used to guide the summarization process.
        output_path (str): The file path where the generated MP3 should be saved.
    """

    def __init__(self, prompt: str, file_source: str, config: dict):
        """
        Initializes the SmartScraper with a prompt, URL, and language model configuration.
        """
        self.prompt = prompt
        self.file_source = file_source
        self.input_key = "url" if "http" in file_source else "local_dir"
        self.llm_model = self._create_llm(config["llm"])
        self.output_path = config.get("output_path", "output.mp3")
        self.text_to_speech_model = OpenAITextToSpeech(config["tts_model"])
        self.graph = self._create_graph()

    def _create_llm(self, llm_config: dict):
        """
        Creates an instance of the ChatOpenAI class with the provided language model configuration.

        Returns:
            ChatOpenAI: An instance of the ChatOpenAI class.

        Raises:
            ValueError: If 'api_key' is not provided in llm_config.
        """
        llm_defaults = {
            "temperature": 0,
            "streaming": True
        }
        # Update defaults with any LLM parameters that were provided
        llm_params = {**llm_defaults, **llm_config}
        # Ensure the api_key is set, raise an error if it's not
        if "api_key" not in llm_params:
            raise ValueError("LLM configuration must include an 'api_key'.")
        # select the model based on the model name
        if "gpt-" in llm_params["model"]:
            return OpenAI(llm_params)
        elif "gemini" in llm_params["model"]:
            return Gemini(llm_params)
        else:
            raise ValueError("Model not supported")

    def _create_graph(self):
        """
        Creates the graph of nodes representing the workflow for web scraping.

        Returns:
            BaseGraph: An instance of the BaseGraph class.
        """
        # define the nodes for the graph
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
            model_config={"llm_model": self.llm_model},
        )
        generate_answer_node = GenerateAnswerNode(
            input="user_prompt & (relevant_chunks | parsed_doc | doc)",
            output=["answer"],
            model_config={"llm_model": self.llm_model},
        )
        text_to_speech_node = TextToSpeechNode(
            input="answer",
            output=["audio"],
            model_config={"tts_model": self.text_to_speech_model},
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
        Executes the scraping process by running the graph and returns the extracted information.

        Returns:
            str: The answer extracted from the web page, corresponding to the given prompt.
        """
        inputs = {"user_prompt": self.prompt, self.input_key: self.file_source}
        final_state = self.graph.execute(inputs)

        audio = final_state.get("audio", None)
        if not audio:
            raise ValueError("No audio generated from the text.")
        save_audio_from_bytes(audio, self.output_path)
        print(f"Audio saved to {self.output_path}")

        return final_state
