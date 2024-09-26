"""
This module contains the code generation functions for code correction for different types errors.
"""
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json
from ..prompts import (
    TEMPLATE_SYNTAX_CODE_GENERATION, TEMPLATE_EXECUTION_CODE_GENERATION,
    TEMPLATE_VALIDATION_CODE_GENERATION, TEMPLATE_SEMANTIC_CODE_GENERATION
)

def syntax_focused_code_generation(state: dict, analysis: str, llm_model) -> str:
    prompt = PromptTemplate(template=TEMPLATE_SYNTAX_CODE_GENERATION, input_variables=["analysis", "generated_code"])
    chain = prompt | llm_model | StrOutputParser()
    return chain.invoke({
        "analysis": analysis,
        "generated_code": state["generated_code"]
    })

def execution_focused_code_generation(state: dict, analysis: str, llm_model) -> str:
    prompt = PromptTemplate(template=TEMPLATE_EXECUTION_CODE_GENERATION, input_variables=["analysis", "generated_code"])
    chain = prompt | llm_model | StrOutputParser()
    return chain.invoke({
        "analysis": analysis,
        "generated_code": state["generated_code"]
    })

def validation_focused_code_generation(state: dict, analysis: str, llm_model) -> str:
    prompt = PromptTemplate(template=TEMPLATE_VALIDATION_CODE_GENERATION, input_variables=["analysis", "generated_code", "json_schema"])
    chain = prompt | llm_model | StrOutputParser()
    return chain.invoke({
        "analysis": analysis,
        "generated_code": state["generated_code"],
        "json_schema": state["json_schema"]
    })
    
def semantic_focused_code_generation(state: dict, analysis: str, llm_model) -> str:
    prompt = PromptTemplate(template=TEMPLATE_SEMANTIC_CODE_GENERATION, input_variables=["analysis", "generated_code", "generated_result", "reference_result"])
    chain = prompt | llm_model | StrOutputParser()
    return chain.invoke({
        "analysis": analysis,
        "generated_code": state["generated_code"],
        "generated_result": json.dumps(state["execution_result"], indent=2),
        "reference_result": json.dumps(state["reference_answer"], indent=2)
    })