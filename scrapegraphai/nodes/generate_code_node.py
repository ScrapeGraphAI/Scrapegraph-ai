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
        
        self.max_iterations = node_config.get("max_iterations", {
            "overall": 10,
            "syntax": 3,
            "execution": 3,
            "validation": 3
        })
        
        self.output_schema = node_config.get("schema").schema() #          get JSON output schema

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

        input_keys = self.get_input_keys(state)
        
        input_data = [state[key] for key in input_keys]
        
        user_prompt = input_data[0] #       get user prompt
        refined_prompt = input_data[1] #    get refined prompt
        html_info = input_data[2] #         get html analysis
        reduced_html = input_data[3] #      get html code
        answer = input_data[4] #            get answer generated from the generate answer node for verification
        
        self.raw_html = state['original_html'][0].page_content
        
        simplefied_schema = str(transform_schema(self.output_schema)) #          get JSON output schema
        
        reasoning_state = {
            "user_input": user_prompt,
            "json_schema": simplefied_schema,
            "initial_analysis": refined_prompt,
            "html_code": reduced_html,
            "html_analysis": html_info,
            "generated_code": "",
            "execution_result": None,
            "errors": {
                "syntax": [],
                "execution": [],
                "validation": []
            },
            "iteration": 0
        }
    
    
        final_state = self.overall_reasoning_loop(reasoning_state)
        
        state.update({self.output[0]: final_state["generated_code"]})
        return state
    
    def overall_reasoning_loop(self, state: dict) -> dict:
        
        state["generated_code"] = self.generate_initial_code(state)
        
        while state["iteration"] < self.max_iterations["overall"]:
            state["iteration"] += 1
            
            state = self.syntax_reasoning_loop(state)
            if state["errors"]["syntax"]:
                continue
            
            state = self.execution_reasoning_loop(state)
            if state["errors"]["execution"]:
                continue
            
            state = self.validation_reasoning_loop(state)
            if state["errors"]["validation"]:
                continue
            
            # If we've made it here, the code is valid and produces the correct output
            break
        
        return state
    
    def syntax_reasoning_loop(self, state: dict) -> dict:
        for _ in range(self.max_iterations["syntax"]):
            syntax_valid, syntax_message = self.syntax_check(state["generated_code"])
            if syntax_valid:
                state["errors"]["syntax"] = []
                return state
            
            state["errors"]["syntax"] = [syntax_message]
            analysis = self.syntax_focused_analysis(state)
            state["generated_code"] = self.syntax_focused_code_generation(state, analysis)
        return state
    
    def execution_reasoning_loop(self, state: dict, raw_html: str) -> dict:
        for _ in range(self.max_iterations["execution"]):
            execution_success, execution_result = self.create_sandbox_and_execute(state["generated_code"], raw_html)
            if execution_success:
                state["execution_result"] = execution_result
                state["errors"]["execution"] = []
                return state
            
            state["errors"]["execution"] = [execution_result]
            analysis = self.execution_focused_analysis(state)
            state["generated_code"] = self.execution_focused_code_generation(state, analysis)
        return state
    
    def validation_reasoning_loop(self, state: dict) -> dict:
        for _ in range(self.max_iterations["validation"]):
            validation, errors = self.validate_dict(state["execution_result"], self.output_schema.schema())
            if validation:
                state["errors"]["validation"] = []
                return state
            
            state["errors"]["validation"] = errors
            analysis = self.validation_focused_analysis(state)
            state["generated_code"] = self.validation_focused_code_generation(state, analysis)
        return state
    
    def generate_initial_code(self, state: dict) -> str:
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
        
        prompt = PromptTemplate(
            template=template_code_generator,
            partial_variables={
                "user_input": state["user_input"],
                "json_schema": state["json_schema"],
                "initial_analysis": state["initial_analysis"],
                "html_code": state["html_code"],
                "html_analysis": state["html_analysis"]
            })

        output_parser = StrOutputParser()

        chain =  prompt | self.llm_model | output_parser
        generated_code = chain.invoke({})
        return generated_code
    
    def syntax_focused_analysis(self, state: dict) -> str:
        template = """
        The current code has encountered a syntax error. Here are the details:
        
        Current Code:
        ```python
        {generated_code}
        ```
        
        Syntax Error:
        {errors}
        
        Please analyze in detail the syntax error and suggest a fix. Focus only on correcting the syntax issue while ensuring the code still meets the original requirements.
        
        Provide your analysis and suggestions for fixing the error. DO NOT generate any code in your response.
        """
        
        prompt = PromptTemplate(template=template, input_variables=["generated_code", "errors"])
        chain = prompt | self.llm_model | StrOutputParser()
        return chain.invoke({
            "generated_code": state["generated_code"],
            "errors": state["errors"]["syntax"]
        })
    
    def syntax_focused_code_generation(self, state: dict, analysis: str) -> str:
        template = """
        Based on the following analysis of a syntax error, please generate the corrected code, following the suggested fix.:

        Error Analysis:
        {analysis}

        Original Code:
        ```python
        {generated_code}
        ```

        Generate the corrected code, applying the suggestions from the analysis. Output ONLY the corrected Python code, WITHOUT ANY ADDITIONAL TEXT.
        """

        prompt = PromptTemplate(template=template, input_variables=["analysis", "generated_code"])
        chain = prompt | self.llm_model | StrOutputParser()
        return chain.invoke({
            "analysis": analysis,
            "generated_code": state["generated_code"]
        })
    
    def execution_focused_analysis(self, state: dict) -> str:
        template = """
        The current code has encountered an execution error. Here are the details:
        
        **Current Code**:
        ```python
        {generated_code}
        ```
        
        **Execution Error**:
        {errors}
        
        **HTML Code**:
        ```html
        {html_code}
        ```

        **HTML Structure Analysis**:
        {html_analysis}
        
        Please analyze the execution error and suggest a fix. Focus only on correcting the execution issue while ensuring the code still meets the original requirements and maintains correct syntax.
        The suggested fix should address the execution error and ensure the function can successfully extract the required data from the provided HTML structure. Be sure to be precise and specific in your analysis.
        
        Provide your analysis and suggestions for fixing the error. DO NOT generate any code in your response.
        """
        
        prompt = PromptTemplate(template=template, input_variables=["generated_code", "errors", "html_code", "html_analysis"])
        chain = prompt | self.llm_model | StrOutputParser()
        return chain.invoke({
            "generated_code": state["generated_code"],
            "errors": state["errors"]["execution"],
            "html_code": state["html_code"],
            "html_analysis": state["html_analysis"]
        })
    
    def execution_focused_code_generation(self, state: dict, analysis: str) -> str:
        template = """
        Based on the following analysis of an execution error, please generate the corrected code:

        Error Analysis:
        {analysis}

        Original Code:
        ```python
        {generated_code}
        ```

        Generate the corrected code, applying the suggestions from the analysis. Output ONLY the corrected Python code, WITHOUT ANY ADDITIONAL TEXT.
        """

        prompt = PromptTemplate(template=template, input_variables=["analysis", "generated_code"])
        chain = prompt | self.llm_model | StrOutputParser()
        return chain.invoke({
            "analysis": analysis,
            "generated_code": state["generated_code"]
        })
    
    def validation_focused_analysis(self, state: dict) -> str:
        template = """
        The current code's output does not match the required schema. Here are the details:
        
        Current Code:
        ```python
        {generated_code}
        ```
        
        Validation Errors:
        {errors}
        
        Required Schema:
        ```json
        {json_schema}
        ```
        
        Current Output:
        {execution_result}
        
        Please analyze the validation errors and suggest fixes. Focus only on correcting the output to match the required schema while ensuring the code maintains correct syntax and execution.
        
        Provide your analysis and suggestions for fixing the error. DO NOT generate any code in your response.
        """
        
        prompt = PromptTemplate(template=template, input_variables=["generated_code", "errors", "json_schema", "execution_result"])
        chain = prompt | self.llm_model | StrOutputParser()
        return chain.invoke({
            "generated_code": state["generated_code"],
            "errors": state["errors"]["validation"],
            "json_schema": state["json_schema"],
            "execution_result": state["execution_result"]
        })
    
    def validation_focused_code_generation(self, state: dict, analysis: str) -> str:
        template = """
        Based on the following analysis of a validation error, please generate the corrected code:

        Error Analysis:
        {analysis}

        Original Code:
        ```python
        {generated_code}
        ```

        Required Schema:
        ```json
        {json_schema}
        ```

        Generate the corrected code, applying the suggestions from the analysis and ensuring the output matches the required schema. Output ONLY the corrected Python code, WITHOUT ANY ADDITIONAL TEXT.
        """

        prompt = PromptTemplate(template=template, input_variables=["analysis", "generated_code", "json_schema"])
        chain = prompt | self.llm_model | StrOutputParser()
        return chain.invoke({
            "analysis": analysis,
            "generated_code": state["generated_code"],
            "json_schema": state["json_schema"]
        })
    
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