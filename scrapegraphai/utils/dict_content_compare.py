"""
This module contains utility functions for comparing the content of two dictionaries.

Functions:
- normalize_dict: Recursively normalizes the values in a dictionary, 
converting strings to lowercase and stripping whitespace.
- normalize_list: Recursively normalizes the values in a list, 
converting strings to lowercase and stripping whitespace.
- are_content_equal: Compares two dictionaries for semantic equality after normalization.
"""
from typing import Any, Dict, List

def normalize_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively normalizes the values in a dictionary.

    Args:
        d (Dict[str, Any]): The dictionary to normalize.

    Returns:
        Dict[str, Any]: A normalized dictionary with strings converted 
        to lowercase and stripped of whitespace.
    """
    normalized = {}
    for key, value in d.items():
        if isinstance(value, str):
            normalized[key] = value.lower().strip()
        elif isinstance(value, dict):
            normalized[key] = normalize_dict(value)
        elif isinstance(value, list):
            normalized[key] = normalize_list(value)
        else:
            normalized[key] = value
    return normalized

def normalize_list(lst: List[Any]) -> List[Any]:
    """
    Recursively normalizes the values in a list.

    Args:
        lst (List[Any]): The list to normalize.

    Returns:
        List[Any]: A normalized list with strings converted to lowercase and stripped of whitespace.
    """
    return [
        normalize_dict(item) if isinstance(item, dict)
        else normalize_list(item) if isinstance(item, list)
        else item.lower().strip() if isinstance(item, str)
        else item
        for item in lst
    ]

def are_content_equal(generated_result: Dict[str, Any], reference_result: Dict[str, Any]) -> bool:
    """
    Compares two dictionaries for semantic equality after normalization.

    Args:
        generated_result (Dict[str, Any]): The generated result dictionary.
        reference_result (Dict[str, Any]): The reference result dictionary.

    Returns:
        bool: True if the normalized dictionaries are equal, False otherwise.
    """
    return normalize_dict(generated_result) == normalize_dict(reference_result)
