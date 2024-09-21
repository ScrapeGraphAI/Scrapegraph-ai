"""
HtmlAnalyzerNode Module
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
from ..utils import reduce_html


class HtmlAnalyzerNode(BaseNode):
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
        node_name: str = "HtmlAnalyzer",
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

        template_html_analysis = """
        Task: Your job is to analyze the provided HTML code in relation to the initial scraping task analysis and provide all the necessary HTML information useful for implementing a function that extracts data from the given HTML string.
        
        **Initial Analysis**:
        {initial_analysis}

        **HTML Code**:
        ```html
        {html_code}
        ```

        **HTML Analysis Instructions**:
        1. Examine the HTML code and identify elements, classes, or IDs that correspond to each required data field mentioned in the Initial Analysis.
        2. Look for patterns or repeated structures that could indicate multiple items (e.g., product listings).
        3. Note any nested structures or relationships between elements that are relevant to the data extraction task.
        4. Discuss any additional considerations based on the specific HTML layout that are crucial for accurate data extraction.
        5. Recommend the specific strategy to use for scraping the content, remeber.

        **Important Notes**:
        - The function that the code generator is gonig to implement will receive the HTML as a string parameter, not as a live webpage.
        - No web scraping, automation, or handling of dynamic content is required.
        - The analysis should focus solely on extracting data from the static HTML provided.
        - Be precise and specific in your analysis, as the code generator will, possibly, not have access to the full HTML context.
        
        This HTML analysis will be used to guide the final code generation process for a function that extracts data from the given HTML string.
        Please provide only the analysis with relevant, specific information based on this HTML code. Avoid vague statements and focus on exact details needed for accurate data extraction.
        
        Focus on providing a concise, step-by-step analysis of the HTML structure and the key elements needed for data extraction. Do not include any code examples or implementation logic. Keep the response focused and avoid general statements.**
        
        **HTML Analysis for Data Extraction**:
        """
        
        template_html_analysis_with_context = """
        Task: Your job is to analyze the provided HTML code in relation to the initial scraping task analysis and the additional context the user provided and provide all the necessary HTML information useful for implementing a function that extracts data from the given HTML string.
        
        **Initial Analysis**:
        {initial_analysis}

        **HTML Code**:
        ```html
        {html_code}
        ```
        
        **Additional Context**:
        {additional_context}

        **HTML Analysis Instructions**:
        1. Examine the HTML code and identify elements, classes, or IDs that correspond to each required data field mentioned in the Initial Analysis.
        2. Look for patterns or repeated structures that could indicate multiple items (e.g., product listings).
        3. Note any nested structures or relationships between elements that are relevant to the data extraction task.
        4. Discuss any additional considerations based on the specific HTML layout that are crucial for accurate data extraction.
        5. Recommend the specific strategy to use for scraping the content, remeber.

        **Important Notes**:
        - The function that the code generator is gonig to implement will receive the HTML as a string parameter, not as a live webpage.
        - No web scraping, automation, or handling of dynamic content is required.
        - The analysis should focus solely on extracting data from the static HTML provided.
        - Be precise and specific in your analysis, as the code generator will, possibly, not have access to the full HTML context.
        
        This HTML analysis will be used to guide the final code generation process for a function that extracts data from the given HTML string.
        Please provide only the analysis with relevant, specific information based on this HTML code. Avoid vague statements and focus on exact details needed for accurate data extraction.
        
        Focus on providing a concise, step-by-step analysis of the HTML structure and the key elements needed for data extraction. Do not include any code examples or implementation logic. Keep the response focused and avoid general statements.**
        
        **HTML Analysis for Data Extraction**:
        """
        
        self.logger.info(f"--- Executing {self.node_name} Node ---")

        input_keys = self.get_input_keys(state)
        
        input_data = [state[key] for key in input_keys]
        refined_prompt = input_data[0] #                        get refined user prompt
        html = input_data[1] #                                  get HTML code
        
        reduced_html = reduce_html(html[0].page_content, self.node_config.get("reduction", 0)) #                reduce HTML code
        
        if self.additional_info is not None: #              use additional context if present
            prompt = PromptTemplate(
                template=template_html_analysis_with_context,
                partial_variables={"initial_analysis": refined_prompt,
                                    "html_code": reduced_html,
                                    "additional_context": self.additional_info})
        else:
            prompt = PromptTemplate(
                template=template_html_analysis,
                partial_variables={"initial_analysis": refined_prompt,
                                    "html_code": reduced_html})

        output_parser = StrOutputParser()

        chain =  prompt | self.llm_model | output_parser
        html_analysis = chain.invoke({})

        state.update({self.output[0]: html_analysis, self.output[1]: reduced_html})
        return state

