import tiktoken
from tqdm import tqdm
from typing import List
from .getter import _get_function
from langchain_openai import ChatOpenAI
from .dictionaries import schema_example
from langchain.prompts import PromptTemplate
from .token_calculator import truncate_text_tokens
from langchain_core.output_parsers import JsonOutputParser

EMBEDDING_ENCODING = 'cl100k_base'

def _getJson(key: str, link: str,  model_name:str, encoding_name_chunk: str = EMBEDDING_ENCODING) -> str:
    """
    Function that creates a JSON schema given a link
    Args:
        key (str): openai key
        link (str): link to analyze
        model_name (str): The name of the openai language model to be used.
        encoding_name_chunk (str):  The name of the encoding to be used (default: EMBEDDING_ENCODING).
    Returns:
        str: the HTML schema of the website
    """
    model = ChatOpenAI(temperature=0, openai_api_key=key)
    parser = JsonOutputParser()

    html = _get_function(link)

    chunks = truncate_text_tokens(html, model=model_name, encoding_name=encoding_name_chunk)

    progress_bar = tqdm(total=len(chunks), desc="Sending chunks")

    result = []

    for chunk in chunks:
        prompt = PromptTemplate(
            template="You are a website scraper and you want to extract information in a schema like the example provided. Write a dictionary where the key is the section and the value is the type.\n{format_instructions}\n{query}\n. Example: {example}",
            input_variables=["query"],
            partial_variables={
                "format_instructions": parser.get_format_instructions(),
                "example": str(schema_example),
            },
        )

        chain = prompt | model | parser

        result.append(chain.invoke({"query": chunk}))

        progress_bar.update(1)

    progress_bar.close()

    if(len(result)>1):
        prompt = PromptTemplate(
            template="You are a website scraper and you have to merge the given schemas without repetitions.\n{format_instructions}}\n. Example: {to_merge}",
            input_variables=["to_merge"],
            partial_variables={"format_instructions": parser.get_format_instructions()
                            },
        )
 
        chain = prompt | model | parser

        result = chain.invoke({"query": str(result)})

    return result
