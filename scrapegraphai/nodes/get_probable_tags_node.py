"""
Module for proobable tags
"""
from langchain.output_parsers import CommaSeparatedListOutputParser
from langchain.prompts import PromptTemplate
from .base_node import BaseNode


class GetProbableTagsNode(BaseNode):
    """
    A node that utilizes a language model to identify probable HTML tags within a document that 
    are likely to contain the information relevant to a user's query. This node generates a prompt
    describing the task, submits it to the language model, and processes the output to produce a 
    list of probable tags.

    Attributes:
        llm: An instance of a language model client, configured for generating tag predictions.
        node_name (str): The unique identifier name for the node,
        defaulting to "GetProbableTagsNode".
        node_type (str): The type of the node, set to "node" indicating a standard operational node.

    Args:
        llm: An instance of the language model client (e.g., ChatOpenAI) used for tag predictions.
        node_name (str, optional): The unique identifier name for the node. 
        Defaults to "GetProbableTagsNode".

    Methods:
        execute(state): Processes the user's input and the URL from the state to generate a list of 
                        probable HTML tags, updating the state with these tags under the 'tags' key.
    """

    def __init__(self, llm, node_name: str):
        """
        Initializes the GetProbableTagsNode with a language model client and a node name.
        Args:
            llm (OpenAIImageToText): An instance of the OpenAIImageToText class.
            node_name (str): name of the node
        """
        super().__init__(node_name, "node")
        self.llm = llm

    def execute(self, state: dict):
        """
        Generates a list of probable HTML tags based on the user's input and updates the state 
        with this list. The method constructs a prompt for the language model, submits it, and 
        parses the output to identify probable tags.

        Args:
            state (dict): The current state of the graph, expected to contain 'user_input', 'url',
                          and optionally 'document' within 'keys'.

        Returns:
            dict: The updated state with the 'tags' key containing a list of probable HTML tags.

        Raises:
            KeyError: If 'user_input' or 'url' is not found in the state, indicating that the
                      necessary information for generating tag predictions is missing.
        """

        print("---GETTING PROBABLE TAGS---")
        try:
            user_input = state["user_input"]
            url = state["url"]
        except KeyError as e:
            print(f"Error: {e} not found in state.")
            raise

        output_parser = CommaSeparatedListOutputParser()
        format_instructions = output_parser.get_format_instructions()

        template = """You are a website scraper that knows all the types of html tags.
         You are now asked to list all the html tags where you think you can find the information of the asked question.\n 
         {format_instructions} \n  The webpage is: {webpage} \n The asked question is the following: {question}
        """

        tag_prompt = PromptTemplate(
            template=template,
            input_variables=["question"],
            partial_variables={
                "format_instructions": format_instructions, "webpage": url},
        )

        # Execute the chain to get probable tags
        tag_answer = tag_prompt | self.llm | output_parser
        probable_tags = tag_answer.invoke({"question": user_input})

        print("Possible tags: ", *probable_tags)

        # Update the dictionary with probable tags
        state.update({"tags": probable_tags})
        return state
