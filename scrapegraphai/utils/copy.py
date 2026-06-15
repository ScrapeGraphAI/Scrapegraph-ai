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


def safe_deepcopy(obj: Any, memo: dict = None) -> Any:
    """
    Safely create a deep copy of an object, handling special cases.

    This performs a true recursive deep copy of containers and generic
    objects (recursing into ``__dict__``) while tracking already-copied
    objects in a ``memo`` dict so circular references are preserved
    instead of causing infinite recursion. Objects that cannot be deep
    or shallow copied (e.g. boto3 clients, thread locks) are returned
    as-is.

    Args:
        obj: Object to copy
        memo: Internal memoization dict mapping id(obj) -> copy, used to
            handle circular references.

    Returns:
        Deep copy of the object

    Raises:
        DeepCopyError: If object cannot be deep copied
    """
    if memo is None:
        memo = {}

    # Return already-copied objects to preserve identity / cycles.
    obj_id = id(obj)
    if obj_id in memo:
        return memo[obj_id]

    # Handle immutable / atomic cases first.
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj

    if isinstance(obj, list):
        new_list = []
        memo[obj_id] = new_list
        for v in obj:
            new_list.append(safe_deepcopy(v, memo))
        return new_list

    if isinstance(obj, set):
        new_set = set()
        memo[obj_id] = new_set
        for v in obj:
            new_set.add(safe_deepcopy(v, memo))
        return new_set

    if isinstance(obj, dict):
        new_dict = {}
        memo[obj_id] = new_dict
        for k, v in obj.items():
            new_dict[safe_deepcopy(k, memo)] = safe_deepcopy(v, memo)
        return new_dict

    if isinstance(obj, tuple):
        new_tuple = tuple(safe_deepcopy(v, memo) for v in obj)
        memo[obj_id] = new_tuple
        return new_tuple

    if isinstance(obj, frozenset):
        new_frozenset = frozenset(safe_deepcopy(v, memo) for v in obj)
        memo[obj_id] = new_frozenset
        return new_frozenset

    if is_boto3_client(obj):
        return obj

    # Generic objects: try a true deep copy first, then fall back to a
    # shallow copy, then to returning the object unchanged. Only raise
    # if nothing works.
    try:
        new_obj = copy.deepcopy(obj, memo)
        memo[obj_id] = new_obj
        return new_obj
    except Exception:
        pass

    try:
        new_obj = copy.copy(obj)
        memo[obj_id] = new_obj
        return new_obj
    except Exception:
        pass

    # As a last resort, recurse into the object's own __dict__ so that
    # mutable attributes are deep copied even when copy.copy/deepcopy fail.
    if hasattr(obj, "__dict__"):
        try:
            cls = obj.__class__
            new_obj = cls.__new__(cls)
            memo[obj_id] = new_obj
            for attr, value in obj.__dict__.items():
                setattr(new_obj, attr, safe_deepcopy(value, memo))
            return new_obj
        except Exception as e:
            raise DeepCopyError(
                f"Cannot deep copy object of type {type(obj)}"
            ) from e

    raise DeepCopyError(f"Cannot deep copy object of type {type(obj)}")
