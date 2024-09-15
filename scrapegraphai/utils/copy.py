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
    Attempts to create a deep copy of the object using `copy.deepcopy`
    whenever possible. If that fails, it falls back to custom deep copy
    logic. If that also fails, it raises a `DeepCopyError`.

    Args:
        obj (Any): The object to be copied, which can be of any type.

    Returns:
        Any: A deep copy of the object if possible; otherwise, a shallow
        copy if deep copying fails; if neither is possible, the original
        object is returned.
    Raises:
        DeepCopyError: If the object cannot be deep-copied or shallow-copied.
    """

    try:

        return copy.deepcopy(obj)
    except (TypeError, AttributeError) as e:

        if isinstance(obj, dict):
            new_obj = {}

            for k, v in obj.items():
                new_obj[k] = safe_deepcopy(v)
            return new_obj

        elif isinstance(obj, list):
            new_obj = []

            for v in obj:
                new_obj.append(safe_deepcopy(v))
            return new_obj

        elif isinstance(obj, tuple):
            new_obj = tuple(safe_deepcopy(v) for v in obj)

            return new_obj

        elif isinstance(obj, frozenset):
            new_obj = frozenset(safe_deepcopy(v) for v in obj)
            return new_obj

        elif is_boto3_client(obj):
            return obj

        else:
            try:
                return copy.copy(obj)
            except (TypeError, AttributeError):
                raise DeepCopyError(
                    f"Cannot deep copy the object of type {type(obj)}"
                ) from e
