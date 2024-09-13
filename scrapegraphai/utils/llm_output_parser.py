"""
Custom output parser for the LLM model.
"""
from pydantic import BaseModel as BaseModelV2
from pydantic.v1 import BaseModel as BaseModelV1

def base_model_v1_output_parser(x: BaseModelV1) -> dict:
    """
    Parse the output of an LLM when the schema is a BaseModelv1 and `with_structured_output` is used.

    Args:
        x (BaseModelV2 | BaseModelV1): The output from the LLM model.

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


def base_model_v2_output_parser(x: BaseModelV2) -> dict:
    """
    Parse the output of an LLM when the schema is a BaseModelv2 and `with_structured_output` is used.

    Args:
        x (BaseModelV2): The output from the LLM model.

    Returns:
        dict: The parsed output.
    """
    return x.model_dump()

def typed_dict_output_parser(x: dict) -> dict:
    """
    Parse the output of an LLM when the schema is a TypedDict and `with_structured_output` is used.

    Args:
        x (dict): The output from the LLM model.

    Returns:
        dict: The parsed output.
    """
    return x
