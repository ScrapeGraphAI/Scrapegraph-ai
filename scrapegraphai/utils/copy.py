import copy
from typing import Any, Dict, Optional


def safe_deepcopy(obj: Any, memo: Optional[Dict[int, Any]] = None) -> Any:
    """
    Attempts to create a deep copy of the object using `copy.deepcopy`
    whenever possible. If that fails, it falls back to custom deep copy
    logic or returns the original object.

    Args:
        obj (Any): The object to be copied, which can be of any type.
        memo (Optional[Dict[int, Any]]): A dictionary used to track objects
            that have already been copied to handle circular references.
            If None, a new dictionary is created.

    Returns:
        Any: A deep copy of the object if possible; otherwise, a shallow
        copy if deep copying fails; if neither is possible, the original
        object is returned.
    """

    if memo is None:
        memo = {}

    if id(obj) in memo:
        return memo[id(obj)]

    try:
        # Try to use copy.deepcopy first
        return copy.deepcopy(obj, memo)
    except (TypeError, AttributeError):
        # If deepcopy fails, handle specific types manually

        # Handle dictionaries
        if isinstance(obj, dict):
            new_obj = {}
            memo[id(obj)] = new_obj
            for k, v in obj.items():
                new_obj[k] = safe_deepcopy(v, memo)
            return new_obj

        # Handle lists
        elif isinstance(obj, list):
            new_obj = []
            memo[id(obj)] = new_obj
            for v in obj:
                new_obj.append(safe_deepcopy(v, memo))
            return new_obj

        # Handle tuples (immutable, but might contain mutable objects)
        elif isinstance(obj, tuple):
            new_obj = tuple(safe_deepcopy(v, memo) for v in obj)
            memo[id(obj)] = new_obj
            return new_obj

        # Handle frozensets (immutable, but might contain mutable objects)
        elif isinstance(obj, frozenset):
            new_obj = frozenset(safe_deepcopy(v, memo) for v in obj)
            memo[id(obj)] = new_obj
            return new_obj

        # Handle objects with attributes
        elif hasattr(obj, "__dict__"):
            new_obj = obj.__new__(obj.__class__)
            for attr in obj.__dict__:
                setattr(new_obj, attr, safe_deepcopy(getattr(obj, attr), memo))
            memo[id(obj)] = new_obj
            return new_obj

        # Attempt shallow copy as a fallback
        try:
            return copy.copy(obj)
        except (TypeError, AttributeError):
            pass

        # If all else fails, return the original object
        return obj
