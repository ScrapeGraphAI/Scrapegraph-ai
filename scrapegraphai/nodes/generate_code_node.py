"""
GenerateCodeNode Module
"""
from typing import List, Optional
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel
from langchain_core.utils.pydantic import is_basemodel_subclass
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langchain_mistralai import ChatMistralAI
from langchain_community.chat_models import ChatOllama
import ast
import sys
from io import StringIO
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
from .base_node import BaseNode
from pydantic import ValidationError
from ..utils import transform_schema
from jsonschema import validate, ValidationError


class GenerateCodeNode(BaseNode):
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
        node_name: str = "GenerateCode",
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

        template_code_generator = """
        **Task**: Create a Python function named `extract_data(html: str) -> dict()` using BeautifulSoup that extracts relevant information from the given HTML code string and returns it in a dictionary matching the Desired JSON Output Schema.

        **User's Request**:
        {user_input}

        **Desired JSON Output Schema**:
        ```json
        {json_schema}
        ```

        **Initial Task Analysis**:
        {initial_analysis}

        **HTML Code**:
        ```html
        {html_code}
        ```

        **HTML Structure Analysis**:
        {html_analysis}

        Based on the above analyses, generate the `extract_data(html: str) -> dict()` function that:
        1. Efficiently extracts the required data from the given HTML structure.
        2. Processes and structures the data according to the specified JSON schema.
        3. Returns the structured data as a dictionary.
        
        Your code should be well-commented, explaining the reasoning behind key decisions and any potential areas for improvement or customization.
        
        Use only the following pre-imported libraries:
        - BeautifulSoup from bs4
        - re
        
        **Output ONLY the Python code of the extract_data function, WITHOUT ANY IMPORTS OR ADDITIONAL TEXT.**
        
        **Response**:
        """
        
        self.logger.info(f"--- Executing {self.node_name} Node ---")

        input_keys = self.get_input_keys(state)
        
        input_data = [state[key] for key in input_keys]
        
        user_prompt = input_data[0] #       get user prompt
        refined_prompt = input_data[1] #    get refined prompt
        html_info = input_data[2] #         get html analysis
        reduced_html = input_data[3] #               get html code
        answer = input_data[4] #            get answer generated from the generate answer node for verification
        
        if self.node_config.get("schema", None) is not None:
            
            self.output_schema = self.node_config["schema"].schema() #          get JSON output schema
            self.simplefied_schema = transform_schema(self.output_schema) #          get JSON output schema
        
            prompt = PromptTemplate(
                template=template_code_generator,
                partial_variables={
                    "user_input": user_prompt,
                    "json_schema": str(self.simplefied_schema),
                    "initial_analysis": refined_prompt,
                    "html_code": reduced_html,
                    "html_analysis": html_info
                })

            output_parser = StrOutputParser()

            chain =  prompt | self.llm_model | output_parser
            generated_code = chain.invoke({})
            
            # syntax check
            print("\Checking code syntax...")
            generated_code = self.extract_code(generated_code)
            syntax_valid, syntax_message = self.syntax_check(generated_code)
            
            if not syntax_valid:
                print(f"Syntax not valid: {syntax_message}")
            
            # code execution
            print("\nExecuting code in sandbox...")
            execution_success, execution_result = self.create_sandbox_and_execute(generated_code, reduced_html)
            
            if not execution_success:
                print(f"Executio failed: {execution_result}")
                
            print("Code executed successfully.")
            print(f"Execution result:\n{execution_result}")
            
            validation, errors = self.validate_dict(execution_result, self.output_schema)
            if not validation:
                print(f"Output does not match the schema: {errors}")
            
        
        state.update({self.output[0]: generated_code})
        return state

    def syntax_check(self, code):
        try:
            ast.parse(code)
            return True, "Syntax is correct."
        except SyntaxError as e:
            return False, f"Syntax error: {str(e)}"

    def create_sandbox_and_execute(self, function_code, html_doc):
        # Create a sandbox environment
        sandbox_globals = {
            'BeautifulSoup': BeautifulSoup,
            're': re,
            '__builtins__': __builtins__,
        }
        
        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        try:
            # Execute the function code in the sandbox
            exec(function_code, sandbox_globals)
            
            # Get the extract_data function from the sandbox
            extract_data = sandbox_globals.get('extract_data')
            
            if not extract_data:
                raise NameError("Function 'extract_data' not found in the generated code.")
            
            # Execute the extract_data function with the provided HTML
            result = extract_data(html_doc)
            
            return True, result
        except Exception as e:
            return False, f"Error during execution: {str(e)}"
        finally:
            # Restore stdout
            sys.stdout = old_stdout
            
    def validate_dict(self, data: dict, schema):
        try:
            validate(instance=data, schema=schema)
            return True, None
        except ValidationError as e:
            errors = e.errors()
            return False, errors
    
    def extract_code(self, code: str) -> str:
        # Pattern to match the code inside a code block
        pattern = r'```(?:python)?\n(.*?)```'
        
        # Search for the code block, if present
        match = re.search(pattern, code, re.DOTALL)
        
        # If a code block is found, return the code, otherwise return the entire string
        return match.group(1) if match else code