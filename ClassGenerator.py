import os
from dotenv import load_dotenv
from AmazScraper.pydantic_class import _Response
from AmazScraper.class_creator import create_class
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.pydantic_v1 import Field
from langchain.output_parsers import PydanticOutputParser

load_dotenv()

MY_ENV_VAR = os.getenv('API_KEY')

class Generator:
    def __init__(self, values: list):
        create_class(values)

        self.parser = PydanticOutputParser(pydantic_object=_Response)

        self.prompt = PromptTemplate(
            template="Answer the user query.\n{format_instructions}\n{query}\n",
            input_variables=["query"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()},
        )

        self.model = ChatOpenAI(openai_api_key=MY_ENV_VAR)

        self.chain = self.prompt | self.model | self.parser

    def invocation(self, query_info):
        try:
            result = self.chain.invoke({"query": query_info})
            print(result)
            return result
        except Exception as e:
            print(f"Error: {e}")