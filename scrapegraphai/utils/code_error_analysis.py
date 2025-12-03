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

import json
from typing import Any, Dict, Optional

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field, validator

from ..prompts import (
    TEMPLATE_EXECUTION_ANALYSIS,
    TEMPLATE_SEMANTIC_ANALYSIS,
    TEMPLATE_SYNTAX_ANALYSIS,
    TEMPLATE_VALIDATION_ANALYSIS,
)


class AnalysisError(Exception):
    """Base exception for code analysis errors."""

    pass


class InvalidStateError(AnalysisError):
    """Exception raised when state dictionary is missing required keys."""

    pass


class CodeAnalysisState(BaseModel):
    """Base model for code analysis state validation."""

    generated_code: str = Field(..., description="The generated code to analyze")
    errors: Dict[str, Any] = Field(
        ..., description="Dictionary containing error information"
    )

    @validator("errors")
    def validate_errors(cls, v):
        """Ensure errors dictionary has expected structure."""
        if not isinstance(v, dict):
            raise ValueError("errors must be a dictionary")
        return v


class ExecutionAnalysisState(CodeAnalysisState):
    """Model for execution analysis state validation."""

    html_code: Optional[str] = Field(None, description="HTML code if available")
    html_analysis: Optional[str] = Field(None, description="Analysis of HTML code")

    @validator("errors")
    def validate_execution_errors(cls, v):
        """Ensure errors dictionary contains execution key."""
        super().validate_errors(v)
        if "execution" not in v:
            raise ValueError("errors dictionary must contain 'execution' key")
        return v


class ValidationAnalysisState(CodeAnalysisState):
    """Model for validation analysis state validation."""

    json_schema: Dict[str, Any] = Field(..., description="JSON schema for validation")
    execution_result: Any = Field(..., description="Result of code execution")

    @validator("errors")
    def validate_validation_errors(cls, v):
        """Ensure errors dictionary contains validation key."""
        super().validate_errors(v)
        if "validation" not in v:
            raise ValueError("errors dictionary must contain 'validation' key")
        return v


def get_optimal_analysis_template(error_type: str) -> str:
    """
    Returns the optimal prompt template based on the error type.

    Args:
        error_type (str): Type of error to analyze.

    Returns:
        str: The prompt template text.
    """
    template_registry = {
        "syntax": TEMPLATE_SYNTAX_ANALYSIS,
        "execution": TEMPLATE_EXECUTION_ANALYSIS,
        "validation": TEMPLATE_VALIDATION_ANALYSIS,
        "semantic": TEMPLATE_SEMANTIC_ANALYSIS,
    }
    return template_registry.get(error_type, TEMPLATE_SYNTAX_ANALYSIS)


def syntax_focused_analysis(state: Dict[str, Any], llm_model) -> str:
    """
    Analyzes the syntax errors in the generated code.

    Args:
        state (dict): Contains the 'generated_code' and 'errors' related to syntax.
        llm_model: The language model used for generating the analysis.

    Returns:
        str: The result of the syntax error analysis.

    Raises:
        InvalidStateError: If state is missing required keys.

    Example:
        >>> state = {
            'generated_code': 'print("Hello World")',
            'errors': {'syntax': 'Missing parenthesis'}
        }
        >>> analysis = syntax_focused_analysis(state, mock_llm)
    """
    try:
        # Validate state using Pydantic model
        validated_state = CodeAnalysisState(
            generated_code=state.get("generated_code", ""),
            errors=state.get("errors", {}),
        )

        # Check if syntax errors exist
        if "syntax" not in validated_state.errors:
            raise InvalidStateError("No syntax errors found in state dictionary")

        # Create prompt template and chain
        prompt = PromptTemplate(
            template=get_optimal_analysis_template("syntax"),
            input_variables=["generated_code", "errors"],
        )
        chain = prompt | llm_model | StrOutputParser()

        # Execute chain with validated state
        return chain.invoke(
            {
                "generated_code": validated_state.generated_code,
                "errors": validated_state.errors["syntax"],
            }
        )

    except KeyError as e:
        raise InvalidStateError(f"Missing required key in state dictionary: {e}")
    except Exception as e:
        raise AnalysisError(f"Syntax analysis failed: {str(e)}")


def execution_focused_analysis(state: Dict[str, Any], llm_model) -> str:
    """
    Analyzes the execution errors in the generated code and HTML code.

    Args:
        state (dict): Contains the 'generated_code', 'errors', 'html_code', and 'html_analysis'.
        llm_model: The language model used for generating the analysis.

    Returns:
        str: The result of the execution error analysis.

    Raises:
        InvalidStateError: If state is missing required keys.

    Example:
        >>> state = {
            'generated_code': 'print(x)',
            'errors': {'execution': 'NameError: name "x" is not defined'},
            'html_code': '<div>Test</div>',
            'html_analysis': 'Valid HTML'
        }
        >>> analysis = execution_focused_analysis(state, mock_llm)
    """
    try:
        # Validate state using Pydantic model
        validated_state = ExecutionAnalysisState(
            generated_code=state.get("generated_code", ""),
            errors=state.get("errors", {}),
            html_code=state.get("html_code", ""),
            html_analysis=state.get("html_analysis", ""),
        )

        # Create prompt template and chain
        prompt = PromptTemplate(
            template=get_optimal_analysis_template("execution"),
            input_variables=["generated_code", "errors", "html_code", "html_analysis"],
        )
        chain = prompt | llm_model | StrOutputParser()

        # Execute chain with validated state
        return chain.invoke(
            {
                "generated_code": validated_state.generated_code,
                "errors": validated_state.errors["execution"],
                "html_code": validated_state.html_code,
                "html_analysis": validated_state.html_analysis,
            }
        )

    except KeyError as e:
        raise InvalidStateError(f"Missing required key in state dictionary: {e}")
    except Exception as e:
        raise AnalysisError(f"Execution analysis failed: {str(e)}")


def validation_focused_analysis(state: Dict[str, Any], llm_model) -> str:
    """
    Analyzes the validation errors in the generated code based on a JSON schema.

    Args:
        state (dict): Contains the 'generated_code', 'errors',
        'json_schema', and 'execution_result'.
        llm_model: The language model used for generating the analysis.

    Returns:
        str: The result of the validation error analysis.

    Raises:
        InvalidStateError: If state is missing required keys.

    Example:
        >>> state = {
            'generated_code': 'return {"name": "John"}',
            'errors': {'validation': 'Missing required field: age'},
            'json_schema': {'required': ['name', 'age']},
            'execution_result': {'name': 'John'}
        }
        >>> analysis = validation_focused_analysis(state, mock_llm)
    """
    try:
        # Validate state using Pydantic model
        validated_state = ValidationAnalysisState(
            generated_code=state.get("generated_code", ""),
            errors=state.get("errors", {}),
            json_schema=state.get("json_schema", {}),
            execution_result=state.get("execution_result", {}),
        )

        # Create prompt template and chain
        prompt = PromptTemplate(
            template=get_optimal_analysis_template("validation"),
            input_variables=[
                "generated_code",
                "errors",
                "json_schema",
                "execution_result",
            ],
        )
        chain = prompt | llm_model | StrOutputParser()

        # Execute chain with validated state
        return chain.invoke(
            {
                "generated_code": validated_state.generated_code,
                "errors": validated_state.errors["validation"],
                "json_schema": validated_state.json_schema,
                "execution_result": validated_state.execution_result,
            }
        )

    except KeyError as e:
        raise InvalidStateError(f"Missing required key in state dictionary: {e}")
    except Exception as e:
        raise AnalysisError(f"Validation analysis failed: {str(e)}")


def semantic_focused_analysis(
    state: Dict[str, Any], comparison_result: Dict[str, Any], llm_model
) -> str:
    """
    Analyzes the semantic differences in the generated code based on a comparison result.

    Args:
        state (dict): Contains the 'generated_code'.
        comparison_result (Dict[str, Any]): Contains
        'differences' and 'explanation' of the comparison.
        llm_model: The language model used for generating the analysis.

    Returns:
        str: The result of the semantic error analysis.

    Raises:
        InvalidStateError: If state or comparison_result is missing required keys.

    Example:
        >>> state = {
            'generated_code': 'def add(a, b): return a + b'
        }
        >>> comparison_result = {
            'differences': ['Missing docstring', 'No type hints'],
            'explanation': 'The code is missing documentation'
        }
        >>> analysis = semantic_focused_analysis(state, comparison_result, mock_llm)
    """
    try:
        # Validate state using Pydantic model
        validated_state = CodeAnalysisState(
            generated_code=state.get("generated_code", ""),
            errors=state.get("errors", {}),
        )

        # Validate comparison_result
        if "differences" not in comparison_result:
            raise InvalidStateError("comparison_result missing 'differences' key")
        if "explanation" not in comparison_result:
            raise InvalidStateError("comparison_result missing 'explanation' key")

        # Create prompt template and chain
        prompt = PromptTemplate(
            template=get_optimal_analysis_template("semantic"),
            input_variables=["generated_code", "differences", "explanation"],
        )
        chain = prompt | llm_model | StrOutputParser()

        # Execute chain with validated inputs
        return chain.invoke(
            {
                "generated_code": validated_state.generated_code,
                "differences": json.dumps(comparison_result["differences"], indent=2),
                "explanation": comparison_result["explanation"],
            }
        )

    except KeyError as e:
        raise InvalidStateError(f"Missing required key: {e}")
    except Exception as e:
        raise AnalysisError(f"Semantic analysis failed: {str(e)}")
