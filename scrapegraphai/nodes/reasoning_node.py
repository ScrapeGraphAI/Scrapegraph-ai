"""
PromptRefinerNode Module
"""
from typing import List, Optional
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel
from langchain_core.utils.pydantic import is_basemodel_subclass
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langchain_mistralai import ChatMistralAI
from langchain_community.chat_models import ChatOllama
from tqdm import tqdm
from .base_node import BaseNode
from ..utils import transform_schema

class ReasoningNode(BaseNode):
    """
    ...

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

        self.additional_info = node_config.get("additional_info", None)
        
        self.output_schema = node_config.get("schema")

    def execute(self, state: dict) -> dict:
        """
        ...

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

        TEMPLATE_REASONING = """
        **Task**: Analyze the user's request and the provided JSON schema to guide an LLM in extracting information directly from HTML.

        **User's Request**:
        {user_input}

        **Target JSON Schema**:
        ```json
        {json_schema}
        ```

        **Analysis Instructions**:
        1. **Interpret User Request:** 
        * Identify the key information types or entities the user is seeking.
        * Note any specific attributes, relationships, or constraints mentioned.

        2. **Map to JSON Schema**:
        * For each identified element in the user request, locate its corresponding field in the JSON schema.
        * Explain how the schema structure represents the requested information.
        * Highlight any relevant schema elements not explicitly mentioned in the user's request.

        3. **Data Transformation Guidance**:
        * Provide guidance on any necessary transformations to align extracted data with the JSON schema requirements.

        This analysis will be used to instruct an LLM that has the HTML content in its context. The LLM will use this guidance to extract the information and return it directly in the specified JSON format.

        **Reasoning Output**:
        [Your detailed analysis based on the above instructions]
        """
                
        TEMPLATE_REASONING_WITH_CONTEXT = """
        **Task**: Analyze the user's request, provided JSON schema, and additional context to guide an LLM in extracting information directly from HTML.

        **User's Request**:
        {user_input}

        **Target JSON Schema**:
        ```json
        {json_schema}
        ```

        **Additional Context**:
        {additional_context}

        **Analysis Instructions**:
        1. **Interpret User Request and Context:** 
        * Identify the key information types or entities the user is seeking.
        * Note any specific attributes, relationships, or constraints mentioned.
        * Incorporate insights from the additional context to refine understanding of the task.

        2. **Map to JSON Schema**:
        * For each identified element in the user request, locate its corresponding field in the JSON schema.
        * Explain how the schema structure represents the requested information.
        * Highlight any relevant schema elements not explicitly mentioned in the user's request.

        3. **Extraction Strategy**:
        * Based on the additional context, suggest specific strategies for locating and extracting the required information from the HTML.
        * Highlight any potential challenges or special considerations mentioned in the context.

        4. **Data Transformation Guidance**:
        * Provide guidance on any necessary transformations to align extracted data with the JSON schema requirements.
        * Note any special formatting, validation, or business logic considerations from the additional context.

        This analysis will be used to instruct an LLM that has the HTML content in its context. The LLM will use this guidance to extract the information and return it directly in the specified JSON format.

        **Reasoning Output**:
        [Your detailed analysis based on the above instructions, incorporating insights from the additional context]
        """
        
        user_prompt = state['user_prompt']

        self.simplefied_schema = transform_schema(self.output_schema.schema())
        
        if self.additional_info is not None:
            prompt = PromptTemplate(
                template=TEMPLATE_REASONING_WITH_CONTEXT,
                partial_variables={"user_input": user_prompt,
                                    "json_schema": str(self.simplefied_schema),
                                    "additional_context": self.additional_info})
        else:
            prompt = PromptTemplate(
                template=TEMPLATE_REASONING,
                partial_variables={"user_input": user_prompt,
                                    "json_schema": str(self.simplefied_schema)})

        output_parser = StrOutputParser()

        chain =  prompt | self.llm_model | output_parser
        refined_prompt = chain.invoke({})

        state.update({self.output[0]: refined_prompt})
        return state
