""" 
Module for extracting the summary from the speach
"""
from scrapegraphai.utils.save_audio_from_bytes import save_audio_from_bytes
from ..models import OpenAI, OpenAITextToSpeech
from .base_graph import BaseGraph
from ..nodes import (
    FetchHTMLNode,
    RAGNode,
    GenerateAnswerNode,
    TextToSpeechNode,
)


class SpeechSummaryGraph:
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

    def __init__(self, prompt: str, url: str, llm_config: dict,
                 output_path: str = "website_summary.mp3"):
        """
        Initializes the SmartScraper with a prompt, URL, and language model configuration.
        """
        self.prompt = f"{prompt} - Save the summary in a key called 'summary'."
        self.url = url
        self.llm_config = llm_config
        self.llm = self._create_llm()
        self.output_path = output_path
        self.text_to_speech_model = OpenAITextToSpeech(
            llm_config, model="tts-1", voice="alloy")
        self.graph = self._create_graph()

    def _create_llm(self):
        """
        Creates an instance of the ChatOpenAI class with the provided language model configuration.

        Returns:
            ChatOpenAI: An instance of the ChatOpenAI class.

        Raises:
            ValueError: If 'api_key' is not provided in llm_config.
        """
        llm_defaults = {
            "model_name": "gpt-3.5-turbo",
            "temperature": 0,
            "streaming": True
        }
        # Update defaults with any LLM parameters that were provided
        llm_params = {**llm_defaults, **self.llm_config}
        # Ensure the api_key is set, raise an error if it's not
        if "api_key" not in llm_params:
            raise ValueError("LLM configuration must include an 'api_key'.")
        # Create the ChatOpenAI instance with the provided and default parameters
        return OpenAI(llm_params)

    def _create_graph(self):
        """
        Creates the graph of nodes representing the workflow for web scraping.

        Returns:
            BaseGraph: An instance of the BaseGraph class.
        """
        fetch_html_node = FetchHTMLNode("fetch_html")
        rag_node = RAGNode(self.llm, "rag")
        generate_answer_node = GenerateAnswerNode(self.llm, "generate_answer")
        text_to_speech_node = TextToSpeechNode(
            self.text_to_speech_model, "text_to_speech")

        return BaseGraph(
            nodes={
                fetch_html_node,
                rag_node,
                generate_answer_node,
                text_to_speech_node
            },
            edges={
                (fetch_html_node, rag_node),
                (rag_node, generate_answer_node),
                (generate_answer_node, text_to_speech_node)
            },
            entry_point=fetch_html_node
        )

    def run(self) -> str:
        """
        Executes the scraping process by running the graph and returns the extracted information.

        Returns:
            str: The answer extracted from the web page, corresponding to the given prompt.
        """
        inputs = {"user_input": self.prompt, "url": self.url}
        final_state = self.graph.execute(inputs)

        audio = final_state.get("audio", None)
        if not audio:
            raise ValueError("No audio generated from the text.")
        save_audio_from_bytes(audio, self.output_path)
        print(f"Audio saved to {self.output_path}")

        return final_state
