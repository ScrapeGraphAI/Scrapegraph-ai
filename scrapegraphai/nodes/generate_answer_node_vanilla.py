"""
Module for generating the answer node
"""
# Imports from standard library
from tqdm import tqdm

# Imports from Langchain
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableParallel

# Imports from the library
from .base_node import BaseNode


class GenerateAnswerNodeVanilla(BaseNode):
    """
    A node that generates an answer using a language model (LLM) based on the user's input
    and the content extracted from a webpage. It constructs a prompt from the user's input
    and the scraped content, feeds it to the LLM, and parses the LLM's response to produce
    an answer.

    Attributes:
        llm (ChatOpenAI): An instance of a language model client, configured for generating answers.
        node_name (str): The unique identifier name for the node, defaulting 
        to "GenerateAnswerNode".
        node_type (str): The type of the node, set to "node" indicating a 
        standard operational node.

    Args:
        llm: An instance of the language model client (e.g., ChatOpenAI) used 
        for generating answers.
        node_name (str, optional): The unique identifier name for the node. 
        Defaults to "GenerateAnswerNodeVanilla".

    Methods:
        execute(state): Processes the input and document from the state to generate an answer,
                        updating the state with the generated answer under the 'answer' key.
    """

    def __init__(self, llm, node_name: str):
        """
        Initializes the GenerateAnswerNode with a language model client and a node name.
        Args:
            llm (OpenAIImageToText): An instance of the OpenAIImageToText class.
            node_name (str): name of the node
        """
        super().__init__(node_name, "node")
        self.llm = llm

    def execute(self, state: dict) -> dict:
        """
        Generates an answer by constructing a prompt from the user's input and the scraped
        content, querying the language model, and parsing its response.

        The method updates the state with the generated answer under the 'answer' key.

        Args:
            state (dict): The current state of the graph, expected to contain 'user_input',
                          and optionally 'parsed_document' or 'relevant_chunks' within 'keys'.

        Returns:
            dict: The updated state with the 'answer' key containing the generated answer.

        Raises:
            KeyError: If 'user_input' or 'document' is not found in the state, indicating
                      that the necessary information for generating an answer is missing.
        """

        print("---GENERATING ANSWER---")
        try:
            user_input = state["user_input"]
            document = state["document"][0]
        except KeyError as e:
            print(f"Error: {e} not found in state.")
            raise
        
        context = document

        output_parser = JsonOutputParser()
        format_instructions = output_parser.get_format_instructions()

        template_json = """You are a website scraper and you have just scraped the
        following content from a website.
        You are now asked to answer a question about the content you have scraped.\n {format_instructions} \n
        This is the scraped text:\n
         {context} \n
        Question: {question}
        """

        # Merge the answers from the chunks
        merge_prompt = PromptTemplate(
            template=template_json,
            input_variables=["context", "question"],
            partial_variables={"format_instructions": format_instructions},
        )
        merge_chain = merge_prompt | self.llm | output_parser
        answer = merge_chain.invoke(
            {"context": context, "question": user_input})

        # Update the state with the generated answer
        state.update({"answer": answer})
        return state