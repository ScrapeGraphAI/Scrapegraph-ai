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
from functools import lru_cache
from typing import Any, Dict

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field

from ..prompts import (
    TEMPLATE_EXECUTION_CODE_GENERATION,
    TEMPLATE_SEMANTIC_CODE_GENERATION,
    TEMPLATE_SYNTAX_CODE_GENERATION,
    TEMPLATE_VALIDATION_CODE_GENERATION,
)


class CodeGenerationError(Exception):
    """Base exception for code generation errors."""

    pass


class InvalidCorrectionStateError(CodeGenerationError):
    """Exception raised when state dictionary is missing required keys."""

    pass


class CorrectionState(BaseModel):
    """Base model for code correction state validation."""

    generated_code: str = Field(
        ..., description="The original generated code to correct"
    )

    class Config:
        extra = "allow"


class ValidationCorrectionState(CorrectionState):
    """Model for validation correction state validation."""

    json_schema: Dict[str, Any] = Field(..., description="JSON schema for validation")


class SemanticCorrectionState(CorrectionState):
    """Model for semantic correction state validation."""

    execution_result: Any = Field(..., description="Result of code execution")
    reference_answer: Any = Field(..., description="Reference answer for comparison")


@lru_cache(maxsize=32)
def get_optimal_correction_template(error_type: str) -> str:
    """
    Returns the optimal prompt template for code correction based on the error type.
    Results are cached for performance.

    Args:
        error_type (str): Type of error to correct.

    Returns:
        str: The prompt template text.
    """
    template_registry = {
        "syntax": TEMPLATE_SYNTAX_CODE_GENERATION,
        "execution": TEMPLATE_EXECUTION_CODE_GENERATION,
        "validation": TEMPLATE_VALIDATION_CODE_GENERATION,
        "semantic": TEMPLATE_SEMANTIC_CODE_GENERATION,
    }
    return template_registry.get(error_type, TEMPLATE_SYNTAX_CODE_GENERATION)


def syntax_focused_code_generation(
    state: Dict[str, Any], analysis: str, llm_model
) -> str:
    """
    Generates corrected code based on syntax error analysis.

    Args:
        state (dict): Contains the 'generated_code'.
        analysis (str): The analysis of the syntax errors.
        llm_model: The language model used for generating the corrected code.

    Returns:
        str: The corrected code.

    Raises:
        InvalidCorrectionStateError: If state is missing required keys.

    Example:
        >>> state = {
            'generated_code': 'print("Hello World"'
        }
        >>> analysis = "Missing closing parenthesis in print statement"
        >>> corrected_code = syntax_focused_code_generation(state, analysis, mock_llm)
    """
    try:
        # Validate state using Pydantic model
        validated_state = CorrectionState(
            generated_code=state.get("generated_code", "")
        )

        if not analysis or not isinstance(analysis, str):
            raise InvalidCorrectionStateError("Analysis must be a non-empty string")

        # Create prompt template and chain
        prompt = PromptTemplate(
            template=get_optimal_correction_template("syntax"),
            input_variables=["analysis", "generated_code"],
        )
        chain = prompt | llm_model | StrOutputParser()

        # Execute chain with validated state
        return chain.invoke(
            {"analysis": analysis, "generated_code": validated_state.generated_code}
        )

    except KeyError as e:
        raise InvalidCorrectionStateError(
            f"Missing required key in state dictionary: {e}"
        )
    except Exception as e:
        raise CodeGenerationError(f"Syntax code generation failed: {str(e)}")


def execution_focused_code_generation(
    state: Dict[str, Any], analysis: str, llm_model
) -> str:
    """
    Generates corrected code based on execution error analysis.

    Args:
        state (dict): Contains the 'generated_code'.
        analysis (str): The analysis of the execution errors.
        llm_model: The language model used for generating the corrected code.

    Returns:
        str: The corrected code.

    Raises:
        InvalidCorrectionStateError: If state is missing required keys or analysis is invalid.

    Example:
        >>> state = {
            'generated_code': 'print(x)'
        }
        >>> analysis = "Variable 'x' is not defined before use"
        >>> corrected_code = execution_focused_code_generation(state, analysis, mock_llm)
    """
    try:
        # Validate state using Pydantic model
        validated_state = CorrectionState(
            generated_code=state.get("generated_code", "")
        )

        if not analysis or not isinstance(analysis, str):
            raise InvalidCorrectionStateError("Analysis must be a non-empty string")

        # Create prompt template and chain
        prompt = PromptTemplate(
            template=get_optimal_correction_template("execution"),
            input_variables=["analysis", "generated_code"],
        )
        chain = prompt | llm_model | StrOutputParser()

        # Execute chain with validated state
        return chain.invoke(
            {"analysis": analysis, "generated_code": validated_state.generated_code}
        )

    except KeyError as e:
        raise InvalidCorrectionStateError(
            f"Missing required key in state dictionary: {e}"
        )
    except Exception as e:
        raise CodeGenerationError(f"Execution code generation failed: {str(e)}")


def validation_focused_code_generation(
    state: Dict[str, Any], analysis: str, llm_model
) -> str:
    """
    Generates corrected code based on validation error analysis.

    Args:
        state (dict): Contains the 'generated_code' and 'json_schema'.
        analysis (str): The analysis of the validation errors.
        llm_model: The language model used for generating the corrected code.

    Returns:
        str: The corrected code.

    Raises:
        InvalidCorrectionStateError: If state is missing required keys or analysis is invalid.

    Example:
        >>> state = {
            'generated_code': 'return {"name": "John"}',
            'json_schema': {'required': ['name', 'age']}
        }
        >>> analysis = "The output JSON is missing the required 'age' field"
        >>> corrected_code = validation_focused_code_generation(state, analysis, mock_llm)
    """
    try:
        # Validate state using Pydantic model
        validated_state = ValidationCorrectionState(
            generated_code=state.get("generated_code", ""),
            json_schema=state.get("json_schema", {}),
        )

        if not analysis or not isinstance(analysis, str):
            raise InvalidCorrectionStateError("Analysis must be a non-empty string")

        # Create prompt template and chain
        prompt = PromptTemplate(
            template=get_optimal_correction_template("validation"),
            input_variables=["analysis", "generated_code", "json_schema"],
        )
        chain = prompt | llm_model | StrOutputParser()

        # Execute chain with validated state
        return chain.invoke(
            {
                "analysis": analysis,
                "generated_code": validated_state.generated_code,
                "json_schema": validated_state.json_schema,
            }
        )

    except KeyError as e:
        raise InvalidCorrectionStateError(
            f"Missing required key in state dictionary: {e}"
        )
    except Exception as e:
        raise CodeGenerationError(f"Validation code generation failed: {str(e)}")


def semantic_focused_code_generation(
    state: Dict[str, Any], analysis: str, llm_model
) -> str:
    """
    Generates corrected code based on semantic error analysis.

    Args:
        state (dict): Contains the 'generated_code', 'execution_result', and 'reference_answer'.
        analysis (str): The analysis of the semantic differences.
        llm_model: The language model used for generating the corrected code.

    Returns:
        str: The corrected code.

    Raises:
        InvalidCorrectionStateError: If state is missing required keys or analysis is invalid.

    Example:
        >>> state = {
            'generated_code': 'def add(a, b): return a + b',
            'execution_result': {'result': 3},
            'reference_answer': {'result': 3, 'documentation': 'Adds two numbers'}
        }
        >>> analysis = "The code is missing documentation"
        >>> corrected_code = semantic_focused_code_generation(state, analysis, mock_llm)
    """
    try:
        # Validate state using Pydantic model
        validated_state = SemanticCorrectionState(
            generated_code=state.get("generated_code", ""),
            execution_result=state.get("execution_result", {}),
            reference_answer=state.get("reference_answer", {}),
        )

        if not analysis or not isinstance(analysis, str):
            raise InvalidCorrectionStateError("Analysis must be a non-empty string")

        # Create prompt template and chain
        prompt = PromptTemplate(
            template=get_optimal_correction_template("semantic"),
            input_variables=[
                "analysis",
                "generated_code",
                "generated_result",
                "reference_result",
            ],
        )
        chain = prompt | llm_model | StrOutputParser()

        # Execute chain with validated state
        return chain.invoke(
            {
                "analysis": analysis,
                "generated_code": validated_state.generated_code,
                "generated_result": json.dumps(
                    validated_state.execution_result, indent=2
                ),
                "reference_result": json.dumps(
                    validated_state.reference_answer, indent=2
                ),
            }
        )

    except KeyError as e:
        raise InvalidCorrectionStateError(
            f"Missing required key in state dictionary: {e}"
        )
    except Exception as e:
        raise CodeGenerationError(f"Semantic code generation failed: {str(e)}")
