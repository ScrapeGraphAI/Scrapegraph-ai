"""
This module contains the functions that generate prompts for various types of code error analysis.

Functions:
- syntax_focused_analysis: Focuses on syntax-related errors in the generated code.
- execution_focused_analysis: Focuses on execution-related errors, 
including generated code and HTML analysis.
- validation_focused_analysis: Focuses on validation-related errors, 
considering JSON schema and execution result.
- semantic_focused_analysis: Focuses on semantic differences in 
generated code based on a comparison result.
"""
from typing import Any, Dict
import json
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from ..prompts import (
    TEMPLATE_SYNTAX_ANALYSIS, TEMPLATE_EXECUTION_ANALYSIS,
    TEMPLATE_VALIDATION_ANALYSIS, TEMPLATE_SEMANTIC_ANALYSIS
)

def syntax_focused_analysis(state: dict, llm_model) -> str:
    """
    Analyzes the syntax errors in the generated code.

    Args:
        state (dict): Contains the 'generated_code' and 'errors' related to syntax.
        llm_model: The language model used for generating the analysis.

    Returns:
        str: The result of the syntax error analysis.
    """
    prompt = PromptTemplate(template=TEMPLATE_SYNTAX_ANALYSIS,
                            input_variables=["generated_code", "errors"])
    chain = prompt | llm_model | StrOutputParser()
    return chain.invoke({
        "generated_code": state["generated_code"],
        "errors": state["errors"]["syntax"]
    })

def execution_focused_analysis(state: dict, llm_model) -> str:
    """
    Analyzes the execution errors in the generated code and HTML code.

    Args:
        state (dict): Contains the 'generated_code', 'errors', 'html_code', and 'html_analysis'.
        llm_model: The language model used for generating the analysis.

    Returns:
        str: The result of the execution error analysis.
    """
    prompt = PromptTemplate(template=TEMPLATE_EXECUTION_ANALYSIS,
                            input_variables=["generated_code", "errors",
                                              "html_code", "html_analysis"])
    chain = prompt | llm_model | StrOutputParser()
    return chain.invoke({
        "generated_code": state["generated_code"],
        "errors": state["errors"]["execution"],
        "html_code": state["html_code"],
        "html_analysis": state["html_analysis"]
    })

def validation_focused_analysis(state: dict, llm_model) -> str:
    """
    Analyzes the validation errors in the generated code based on a JSON schema.

    Args:
        state (dict): Contains the 'generated_code', 'errors', 
        'json_schema', and 'execution_result'.
        llm_model: The language model used for generating the analysis.

    Returns:
        str: The result of the validation error analysis.
    """
    prompt = PromptTemplate(template=TEMPLATE_VALIDATION_ANALYSIS,
                            input_variables=["generated_code", "errors", 
                                             "json_schema", "execution_result"])
    chain = prompt | llm_model | StrOutputParser()
    return chain.invoke({
        "generated_code": state["generated_code"],
        "errors": state["errors"]["validation"],
        "json_schema": state["json_schema"],
        "execution_result": state["execution_result"]
    })

def semantic_focused_analysis(state: dict, comparison_result: Dict[str, Any], llm_model) -> str:
    """
    Analyzes the semantic differences in the generated code based on a comparison result.

    Args:
        state (dict): Contains the 'generated_code'.
        comparison_result (Dict[str, Any]): Contains 
        'differences' and 'explanation' of the comparison.
        llm_model: The language model used for generating the analysis.

    Returns:
        str: The result of the semantic error analysis.
    """
    prompt = PromptTemplate(template=TEMPLATE_SEMANTIC_ANALYSIS,
                            input_variables=["generated_code", 
                                             "differences", "explanation"])
    chain = prompt | llm_model | StrOutputParser()
    return chain.invoke({
        "generated_code": state["generated_code"],
        "differences": json.dumps(comparison_result["differences"], indent=2),
        "explanation": comparison_result["explanation"]
    })
