"""
Functions to retrieve the correct output parser and format instructions for the LLM model.
"""
from pydantic import BaseModel as BaseModelV2
from pydantic.v1 import BaseModel as BaseModelV1
from typing import Union, Dict, Any, Type, Callable
from langchain_core.output_parsers import JsonOutputParser

def get_structured_output_parser(schema: Union[Dict[str, Any], Type[BaseModelV1 | BaseModelV2], Type]) -> Callable:
    """
    Get the correct output parser for the LLM model.

    Returns:
        Callable: The output parser function.
    """
    if issubclass(schema, BaseModelV1):
        return _base_model_v1_output_parser
    
    if issubclass(schema, BaseModelV2):
        return _base_model_v2_output_parser

    return _dict_output_parser

def get_pydantic_output_parser(schema: Union[Dict[str, Any], Type[BaseModelV1 | BaseModelV2], Type]) -> JsonOutputParser:
    """
    Get the correct output parser for the LLM model.

    Returns:
        JsonOutputParser: The output parser object.
    """
    if issubclass(schema, BaseModelV1):
        raise ValueError("pydantic.v1 and langchain_core.pydantic_v1 are not supported with this LLM model. Please use pydantic v2 instead.")
    
    if issubclass(schema, BaseModelV2):
        return JsonOutputParser(pydantic_object=schema)

    raise ValueError("The schema is not a pydantic subclass. With this LLM model you must use a pydantic schemas.")

def _base_model_v1_output_parser(x: BaseModelV1) -> dict:
    """
    Parse the output of an LLM when the schema is BaseModelv1.

    Args:
        x (BaseModelV1): The output from the LLM model.

    Returns:
        dict: The parsed output.
    """
    work_dict = x.dict()
    
    # recursive dict parser
    def recursive_dict_parser(work_dict: dict) -> dict:
        dict_keys = work_dict.keys()
        for key in dict_keys:
            if isinstance(work_dict[key], BaseModelV1):
                work_dict[key] = work_dict[key].dict()
                recursive_dict_parser(work_dict[key])
        return work_dict
    
    return recursive_dict_parser(work_dict)


def _base_model_v2_output_parser(x: BaseModelV2) -> dict:
    """
    Parse the output of an LLM when the schema is BaseModelv2.

    Args:
        x (BaseModelV2): The output from the LLM model.

    Returns:
        dict: The parsed output.
    """
    return x.model_dump()

def _dict_output_parser(x: dict) -> dict:
    """
    Parse the output of an LLM when the schema is TypedDict or JsonSchema.

    Args:
        x (dict): The output from the LLM model.

    Returns:
        dict: The parsed output.
    """
    return x
