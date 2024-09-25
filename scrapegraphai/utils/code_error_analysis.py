"""
This module contains the functions that are used to generate the prompts for the code error analysis.
"""
from typing import Any, Dict
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json
from ..prompts import (
    TEMPLATE_SYNTAX_ANALYSIS, TEMPLATE_EXECUTION_ANALYSIS,
    TEMPLATE_VALIDATION_ANALYSIS, TEMPLATE_SEMANTIC_ANALYSIS
)

def syntax_focused_analysis(state: dict, llm_model) -> str:
    prompt = PromptTemplate(template=TEMPLATE_SYNTAX_ANALYSIS, input_variables=["generated_code", "errors"])
    chain = prompt | llm_model | StrOutputParser()
    return chain.invoke({
        "generated_code": state["generated_code"],
        "errors": state["errors"]["syntax"]
    })

def execution_focused_analysis(state: dict, llm_model) -> str:
    prompt = PromptTemplate(template=TEMPLATE_EXECUTION_ANALYSIS, input_variables=["generated_code", "errors", "html_code", "html_analysis"])
    chain = prompt | llm_model | StrOutputParser()
    return chain.invoke({
        "generated_code": state["generated_code"],
        "errors": state["errors"]["execution"],
        "html_code": state["html_code"],
        "html_analysis": state["html_analysis"]
    })

def validation_focused_analysis(state: dict, llm_model) -> str:
    prompt = PromptTemplate(template=TEMPLATE_VALIDATION_ANALYSIS, input_variables=["generated_code", "errors", "json_schema", "execution_result"])
    chain = prompt | llm_model | StrOutputParser()
    return chain.invoke({
        "generated_code": state["generated_code"],
        "errors": state["errors"]["validation"],
        "json_schema": state["json_schema"],
        "execution_result": state["execution_result"]
    })

def semantic_focused_analysis(state: dict, comparison_result: Dict[str, Any], llm_model) -> str:        
    prompt = PromptTemplate(template=TEMPLATE_SEMANTIC_ANALYSIS, input_variables=["generated_code", "differences", "explanation"])
    chain = prompt | llm_model | StrOutputParser()
    return chain.invoke({
        "generated_code": state["generated_code"],
        "differences": json.dumps(comparison_result["differences"], indent=2),
        "explanation": comparison_result["explanation"]
    })