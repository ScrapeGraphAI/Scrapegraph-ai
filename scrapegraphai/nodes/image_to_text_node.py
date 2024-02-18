""" 
Module for creating the basic node
"""
from langchain_openai import ChatOpenAI
from .base_node import BaseNode

from langchain_core.messages import HumanMessage, SystemMessage


class ImageToTextNode(BaseNode):
    """
    An abstract base class for nodes in a graph-based workflow. Each node is 
    intended to perform a specific action when executed as part of the graph's 
    processing flow.

    Attributes:
        node_name (str): A unique identifier for the node.
        node_type (str): Specifies the node's type, which influences how the 
                         node interacts within the graph. Valid values are 
                         "node" for standard nodes and "conditional_node" for 
                         nodes that determine the flow based on conditions.

    Methods:
        execute(state): An abstract method that subclasses must implement. This 
                        method should contain the logic that the node executes 
                        when it is reached in the graph's flow. It takes the 
                        graph's current state as input and returns the updated 
                        state after execution.

    Args:
        node_name (str): The unique identifier name for the node. This name is 
                         used to reference the node within the graph.
        node_type (str): The type of the node, limited to "node" or 
                         "conditional_node". This categorization helps in 
                         determining the node's role and behavior within the 
                         graph.

    Raises:
        ValueError: If the provided `node_type` is not one of the allowed 
                    values ("node" or "conditional_node"), a ValueError is 
                    raised to indicate the incorrect usage.
    """

    def __init__(self, llm, node_name: str = "ParseImageToText"):
        """
        Initialize the node with a unique identifier and a specified node type.

        Args:
            node_name (str): The unique identifier name for the node.
            node_type (str): The type of the node, limited to "node" or "conditional_node".

        Raises:
            ValueError: If node_type is not "node" or "conditional_node".
        """
        super().__init__(node_name, "node")
        self.llm = llm

    def execute(self, state: dict, url: str) -> str:
        """
        Execute the node's logic and return the updated state.
        Args:
            state (dict): The current state of the graph.
            url (str): url of the image where to 
        :return: The updated state after executing this node.
        """
        # Da fixare

        if not self.llm.model_name == "gpt-4-vision-preview":
            raise ValueError("Model is not gpt-4-vision-preview")

        chat = ChatOpenAI(model=self.llm.model_name, max_tokens=256)
        result = chat.invoke(
            [
                HumanMessage(
                    content=[
                        {"type": "text", "text": "What is this image showing"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": url,
                                "detail": "auto",
                            },
                        },
                    ]
                )
            ]
        )

        return result
