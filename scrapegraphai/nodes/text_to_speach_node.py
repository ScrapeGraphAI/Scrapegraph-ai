
"""
Module for parsing the text to voice
"""

from openai import OpenAI
from .base_node import BaseNode


class TextToSpeachNode(BaseNode):
    """
    A node responsible for parsing text content from a document using specified tags and readinf 
    it with the selected voiceq.
    This node enhances the scraping workflow by allowing for targeted extraction of 
    content, thereby optimizing the processing of large HTML documents.

    Attributes:
        node_name (str): The unique identifier name for the node, defaulting to "ParseHTMLNode".
        node_type (str): The type of the node, set to "node" indicating a standard operational node.

    Args:
        node_name (str, optional): The unique identifier name for the node. 
        Defaults to "ParseHTMLNode".

    Methods:
        execute(state): Parses the HTML document contained within the state using 
        the specified tags, if provided, and updates the state with the parsed content.
    """

    def __init__(self, llm, node_name: str = "ParseTextToSpeach"):
        """
        Initializes the ParseHTMLNode with a node name.
        """
        super().__init__(node_name, "node")
        self.llm = llm

    def execute(self, state: dict, text: str, output_path: str = str, model: str = "tts-1", voice="alloy") -> dict:
        """
        Executes the node's logic to parse the HTML document based on specified tags. 
        If tags are provided in the state, the document is parsed accordingly; otherwise, 
        the document remains unchanged. The method updates the state with either the original 
        or parsed document under the 'parsed_document' key.

        Args:
            state (dict): The current state of the graph, expected to contain 
            'document' within 'keys', and optionally 'tags' for targeted parsing.
            text (str):The text you want to read
            outpath_path (strOptional): Path for saving
            model (str): type of model. Possible options: "tts-1" or tts-1-hd
            voice (str): type of the voice. Possible choices: "alloy", "echo", 
            "fable", "onyx", "nova", or "shimmer"

        Returns:
            dict: The updated state with the 'parsed_document' key containing the parsed content,
                  if tags were provided, or the original document otherwise.

        Raises:
            KeyError: If 'document' is not found in the state, indicating that the necessary 
                      information for parsing is missing.
        """
        if output_path is not None:
            try:
                client = OpenAI(
                    api_key=self.llm.openai_api_key)

                response = client.audio.speech.create(
                    model=model,
                    voice=voice,
                    input=text,
                )

                response.stream_to_file(f"{output_path}/output.mp3")
            except Exception as e:
                print(f"Error while saving the audio file: {e}")
        else:
            print("The output path is not specified correctly.")
