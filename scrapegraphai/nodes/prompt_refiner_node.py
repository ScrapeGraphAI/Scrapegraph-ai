"""
PromptRefinerNode Module
"""
from typing import List, Optional
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableParallel
from langchain_core.utils.pydantic import is_basemodel_subclass
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langchain_mistralai import ChatMistralAI
from langchain_community.chat_models import ChatOllama
from tqdm import tqdm
from .base_node import BaseNode


class PromptRefinerNode(BaseNode):
    """
    A node that refine the user prompt with the use of the schema and additional context and
    create a precise prompt in subsequent steps that explicitly link elements in the user's 
    original input to their corresponding representations in the JSON schema.

    Attributes:
        llm_model: An instance of a language model client, configured for generating answers.
        verbose (bool): A flag indicating whether to show print statements during execution.

    Args:
        input (str): Boolean expression defining the input keys needed from the state.
        output (List[str]): List of output keys to be updated in the state.
        node_config (dict): Additional configuration for the node.
        node_name (str): The unique identifier name for the node, defaulting to "GenerateAnswer".
    """

    def __init__(
        self,
        input: str,
        output: List[str],
        node_config: Optional[dict] = None,
        node_name: str = "PromptRefiner",
    ):
        super().__init__(node_name, "node", input, output, 2, node_config)

        self.llm_model = node_config["llm_model"]

        if isinstance(node_config["llm_model"], ChatOllama):
            self.llm_model.format="json"

        self.verbose = (
            True if node_config is None else node_config.get("verbose", False)
        )
        self.force = (
            False if node_config is None else node_config.get("force", False)
        )
        self.script_creator = (
            False if node_config is None else node_config.get("script_creator", False)
        )
        self.is_md_scraper = (
            False if node_config is None else node_config.get("is_md_scraper", False)
        )

        self.additional_info = node_config.get("additional_info")

    def execute(self, state: dict) -> dict:
        """
        Generates an answer by constructing a prompt from the user's input and the scraped
        content, querying the language model, and parsing its response.

        Args:
            state (dict): The current state of the graph. The input keys will be used
                            to fetch the correct data from the state.

        Returns:
            dict: The updated state with the output key containing the generated answer.

        Raises:
            KeyError: If the input keys are not found in the state, indicating
                      that the necessary information for generating an answer is missing.
        """

        self.logger.info(f"--- Executing {self.node_name} Node ---")

        input_keys = self.get_input_keys(state)
        
        input_data = [state[key] for key in input_keys]
        user_prompt = input_data[0]

        if self.node_config.get("schema", None) is not None:

            self.schema = self.node_config["schema"]
            
            if self.additional_info is not None: # add context to the prompt
                pass

            template_prompt_builder = """
            You are tasked with generating a prompt that will guide an LLM in reasoning about how to identify specific elements within an HTML page for data extraction.
            **Input:**
            
            * **User Prompt:** The user's natural language description of the data they want to extract from the HTML page.
            * **JSON Schema:** A JSON schema representing the desired output structure of the extracted data.
            * **Additional Information (Optional):** Any supplementary details provided by the user, such as specific HTML patterns they've observed, known challenges in identifying certain elements, or preferences for particular scraping strategies.

            **Output:**
            """
            
            example_prompts = [
                """
                
                """
            ]
            
            prompt = PromptTemplate(
                template=template_no_chunks_prompt ,
                input_variables=["question"],
                partial_variables={"context": doc,
                                    "format_instructions": format_instructions})
            chain =  prompt | self.llm_model | output_parser
            answer = chain.invoke({"question": user_prompt})

            state.update({self.output[0]: answer})
            return state

        chains_dict = {}
        for i, chunk in enumerate(tqdm(doc, desc="Processing chunks", disable=not self.verbose)):

            prompt = PromptTemplate(
                template=TEMPLATE_CHUNKS,
                input_variables=["question"],
                partial_variables={"context": chunk,
                                "chunk_id": i + 1,
                                "format_instructions": format_instructions})
            chain_name = f"chunk{i+1}"
            chains_dict[chain_name] = prompt | self.llm_model | output_parser

        async_runner = RunnableParallel(**chains_dict)

        batch_results =  async_runner.invoke({"question": user_prompt})

        merge_prompt = PromptTemplate(
                template = template_merge_prompt ,
                input_variables=["context", "question"],
                partial_variables={"format_instructions": format_instructions},
            )

        merge_chain = merge_prompt | self.llm_model | output_parser
        answer = merge_chain.invoke({"context": batch_results, "question": user_prompt})

        state.update({self.output[0]: answer})
        return state
