"""
copy module
"""
import copy
from typing import Any

class DeepCopyError(Exception):
    """
    Custom exception raised when an object cannot be deep-copied.
    """

    pass

def is_boto3_client(obj):
    """ 
    Function for understanding if the script is using boto3 or not
    """
    import sys

    boto3_module = sys.modules.get("boto3")

    if boto3_module:
        try:
            from botocore.client import BaseClient

            return isinstance(obj, BaseClient)
        except (AttributeError, ImportError):
            return False
    return False

def safe_deepcopy(obj: Any) -> Any:
    """
    Safely create a deep copy of an object, handling special cases.
    
    Args:
        obj: Object to copy
        
    Returns:
        Deep copy of the object
        
    Raises:
        DeepCopyError: If object cannot be deep copied
    """
    try:
        # Handle special cases first
        if obj is None or isinstance(obj, (str, int, float, bool)):
            return obj
            
        if isinstance(obj, (list, set)):
            return type(obj)(safe_deepcopy(v) for v in obj)
            
        if isinstance(obj, dict):
            return {k: safe_deepcopy(v) for k, v in obj.items()}
            
        if isinstance(obj, tuple):
            return tuple(safe_deepcopy(v) for v in obj)
            
        if isinstance(obj, frozenset):
            return frozenset(safe_deepcopy(v) for v in obj)
            
        if is_boto3_client(obj):
            return obj
            
        return copy.copy(obj)
        
    except Exception as e:
        raise DeepCopyError(f"Cannot deep copy object of type {type(obj)}") from e
