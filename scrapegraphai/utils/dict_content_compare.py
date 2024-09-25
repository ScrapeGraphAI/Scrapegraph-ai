"""
Utility functions for comparing the content of two dictionaries.
"""
from typing import Any, Dict, List

def normalize_dict(d: Dict[str, Any]) -> Dict[str, Any]:
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
    return [
        normalize_dict(item) if isinstance(item, dict)
        else normalize_list(item) if isinstance(item, list)
        else item.lower().strip() if isinstance(item, str)
        else item
        for item in lst
    ]

def are_content_equal(generated_result: Dict[str, Any], reference_result: Dict[str, Any]) -> bool:
    """Compare two dictionaries for semantic equality."""
    return normalize_dict(generated_result) == normalize_dict(reference_result)