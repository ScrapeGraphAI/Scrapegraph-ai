from .base_node import BaseNode
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

class GenerateAnswerNode(BaseNode):
    def __init__(self, llm, node_name="GenerateAnswerNode"):
        super().__init__(node_name, "node")
        self.llm = llm
        # Initialize any other configurations for the LLM here

    def execute(self, state):
        """
        Generates an answer based on the user's input and the parsed document.
        
        Args:
            state: The current state of the graph, expected to contain
                   'user_input' and 'parsed_document' within 'keys'.
        
        Returns:
            The updated state with 'answer' within 'keys', containing the generated answer.
        """
        
        print("---GENERATE ANSWER---")
        try:
            user_input = state["keys"]["user_input"]
            document = state["keys"]["document"]
        except KeyError as e:
            print(f"Error: {e} not found in state.")
            raise

        parsed_document = state["keys"].get("parsed_document", None)
        relevant_chunks = state["keys"].get("relevant_chunks", None)

        # Use relevant chunks if available, otherwise use the parsed document or the original document
        if relevant_chunks:
            context = relevant_chunks
        elif parsed_document:
            context = parsed_document
        else:
            context = document

        output_parser = JsonOutputParser()
        format_instructions = output_parser.get_format_instructions()

        template = """You are a website scraper and you have just scraped the following content from a website. You are now asked to answer a question about the content you have scraped.\n {format_instructions} \n The content is as follows:
                {context}

                Question: {question}
                """

        schema_prompt = PromptTemplate(
            template=template,
            input_variables=["context", "question"],
            partial_variables={"format_instructions": format_instructions},
        )

        # Chain
        schema_chain = schema_prompt | self.llm | output_parser
        answer = schema_chain.invoke({"context": context, "question": user_input})

        # Update the state with the generated answer
        state["keys"].update({"answer": answer})
        return state
        
