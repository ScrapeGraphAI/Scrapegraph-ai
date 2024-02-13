from .base_node import BaseNode
from langchain.prompts import PromptTemplate
from langchain.output_parsers import CommaSeparatedListOutputParser

class GetProbableTagsNode(BaseNode):
    def __init__(self, llm, node_name="GetProbableTagsNode"):
        super().__init__(node_name, "node")
        self.llm = llm

    def execute(self, state):
        """
        Identifies probable HTML tags from a document based on a user's question.
        
        Args:
            state (dict): The current state of the graph, including 'document', 'user_input', and 'url' within 'keys'.
        
        Returns:
            dict: The updated state with a new key 'tags' within 'keys' containing probable HTML tags.
        """
        
        print("---GET PROBABLE TAGS---")
        # Accessing the nested structure
        try:
            user_input = state["keys"]["user_input"]
            url = state["keys"]["url"]
        except KeyError as e:
            print(f"Error: {e} not found in state.")
            raise

        output_parser = CommaSeparatedListOutputParser()
        format_instructions = output_parser.get_format_instructions()

        template = """You are a website scraper that knows all the types of html tags. You are now asked to list all the html tags where you think you can find the information of the asked question.\n {format_instructions} \n The webpage is: {webpage} \n The asked question is the following:
        {question}
        """

        tag_prompt = PromptTemplate(
            template=template,
            input_variables=["question"],
            partial_variables={"format_instructions": format_instructions, "webpage": url},
        )

        # Execute the chain to get probable tags
        tag_answer = tag_prompt | self.llm | output_parser
        probable_tags = tag_answer.invoke({"question": user_input})

        print("Possible tags: ", *probable_tags)

        # Update the nested 'keys' dictionary with probable tags
        state["keys"].update({"tags": probable_tags})
        return state