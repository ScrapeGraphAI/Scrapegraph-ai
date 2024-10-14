"""
This module contains the functions for code generation to correct different types of errors.

Functions:
- syntax_focused_code_generation: Generates corrected code based on syntax error analysis.
- execution_focused_code_generation: Generates corrected code based on execution error analysis.
- validation_focused_code_generation: Generates corrected code based on 
validation error analysis, considering JSON schema.
- semantic_focused_code_generation: Generates corrected code based on semantic error analysis, 
comparing generated and reference results.
"""
import json
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from ..prompts import (
    TEMPLATE_SYNTAX_CODE_GENERATION, TEMPLATE_EXECUTION_CODE_GENERATION,
    TEMPLATE_VALIDATION_CODE_GENERATION, TEMPLATE_SEMANTIC_CODE_GENERATION
)

def syntax_focused_code_generation(state: dict, analysis: str, llm_model) -> str:
    """
    Generates corrected code based on syntax error analysis.

    Args:
        state (dict): Contains the 'generated_code'.
        analysis (str): The analysis of the syntax errors.
        llm_model: The language model used for generating the corrected code.

    Returns:
        str: The corrected code.
    """
    prompt = PromptTemplate(template=TEMPLATE_SYNTAX_CODE_GENERATION,
                            input_variables=["analysis", "generated_code"])
    chain = prompt | llm_model | StrOutputParser()
    return chain.invoke({
        "analysis": analysis,
        "generated_code": state["generated_code"]
    })

def execution_focused_code_generation(state: dict, analysis: str, llm_model) -> str:
    """
    Generates corrected code based on execution error analysis.

    Args:
        state (dict): Contains the 'generated_code'.
        analysis (str): The analysis of the execution errors.
        llm_model: The language model used for generating the corrected code.

    Returns:
        str: The corrected code.
    """
    prompt = PromptTemplate(template=TEMPLATE_EXECUTION_CODE_GENERATION,
                            input_variables=["analysis", "generated_code"])
    chain = prompt | llm_model | StrOutputParser()
    return chain.invoke({
        "analysis": analysis,
        "generated_code": state["generated_code"]
    })

def validation_focused_code_generation(state: dict, analysis: str, llm_model) -> str:
    """
    Generates corrected code based on validation error analysis.

    Args:
        state (dict): Contains the 'generated_code' and 'json_schema'.
        analysis (str): The analysis of the validation errors.
        llm_model: The language model used for generating the corrected code.

    Returns:
        str: The corrected code.
    """
    prompt = PromptTemplate(template=TEMPLATE_VALIDATION_CODE_GENERATION,
                            input_variables=["analysis", "generated_code", "json_schema"])
    chain = prompt | llm_model | StrOutputParser()
    return chain.invoke({
        "analysis": analysis,
        "generated_code": state["generated_code"],
        "json_schema": state["json_schema"]
    })

def semantic_focused_code_generation(state: dict, analysis: str, llm_model) -> str:
    """
    Generates corrected code based on semantic error analysis.

    Args:
        state (dict): Contains the 'generated_code', 'execution_result', and 'reference_answer'.
        analysis (str): The analysis of the semantic differences.
        llm_model: The language model used for generating the corrected code.

    Returns:
        str: The corrected code.
    """
    prompt = PromptTemplate(template=TEMPLATE_SEMANTIC_CODE_GENERATION,
                            input_variables=["analysis", "generated_code", "generated_result", "reference_result"])
    chain = prompt | llm_model | StrOutputParser()
    return chain.invoke({
        "analysis": analysis,
        "generated_code": state["generated_code"],
        "generated_result": json.dumps(state["execution_result"], indent=2),
        "reference_result": json.dumps(state["reference_answer"], indent=2)
    })
