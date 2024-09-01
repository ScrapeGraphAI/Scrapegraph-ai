import copy
from typing import Any, Dict, Optional
from pydantic.v1 import BaseModel

class DeepCopyError(Exception):
    """Custom exception raised when an object cannot be deep-copied."""
    pass

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
        
        # Try to use copy.deepcopy first
        return copy.deepcopy(obj)
    except (TypeError, AttributeError) as e:
        # If deepcopy fails, handle specific types manually

        # Handle dictionaries
        if isinstance(obj, dict):
            new_obj = {}
            
            for k, v in obj.items():
                new_obj[k] = safe_deepcopy(v)
            return new_obj

        # Handle lists
        elif isinstance(obj, list):
            new_obj = []
            
            for v in obj:
                new_obj.append(safe_deepcopy(v))
            return new_obj

        # Handle tuples (immutable, but might contain mutable objects)
        elif isinstance(obj, tuple):
            new_obj = tuple(safe_deepcopy(v) for v in obj)
            
            return new_obj

        # Handle frozensets (immutable, but might contain mutable objects)
        elif isinstance(obj, frozenset):
            new_obj = frozenset(safe_deepcopy(v) for v in obj)
            return new_obj

        # Handle objects with attributes
        elif hasattr(obj, "__dict__"):
            # If an object cannot be deep copied, then the sub-properties of \
            # the object will not be analyzed and shallow copy will be used directly.
            try:
                return copy.copy(obj)
            except (TypeError, AttributeError):
                raise DeepCopyError(f"Cannot deep copy the object of type {type(obj)}") from e


        # Attempt shallow copy as a fallback
        try:
            return copy.copy(obj)
        except (TypeError, AttributeError):
            raise DeepCopyError(f"Cannot deep copy the object of type {type(obj)}") from e
            
