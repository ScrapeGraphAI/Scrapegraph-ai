import copy
import pytest

# Assuming the custom_deepcopy function is imported or defined above this line
from scrapegraphai.utils.copy import safe_deepcopy


class NormalObject:
    def __init__(self, value):
        self.value = value
        self.nested = [1, 2, 3]

    def __deepcopy__(self, memo):
        raise TypeError("Forcing fallback")


class NonDeepcopyable:
    def __init__(self, value):
        self.value = value

    def __deepcopy__(self, memo):
        raise TypeError("Forcing shallow copy fallback")


class WithoutDict:
    __slots__ = ["value"]

    def __init__(self, value):
        self.value = value

    def __deepcopy__(self, memo):
        raise TypeError("Forcing shallow copy fallback")

    def __copy__(self):
        return self


class NonCopyableObject:
    __slots__ = ["value"]

    def __init__(self, value):
        self.value = value

    def __deepcopy__(self, memo):
        raise TypeError("fail deep copy ")

    def __copy__(self):
        raise TypeError("fail shallow copy")


def test_deepcopy_simple_dict():
    original = {"a": 1, "b": 2, "c": [3, 4, 5]}
    copy_obj = safe_deepcopy(original)
    assert copy_obj == original
    assert copy_obj is not original
    assert copy_obj["c"] is not original["c"]


def test_deepcopy_simple_list():
    original = [1, 2, 3, [4, 5]]
    copy_obj = safe_deepcopy(original)
    assert copy_obj == original
    assert copy_obj is not original
    assert copy_obj[3] is not original[3]


def test_deepcopy_with_tuple():
    original = (1, 2, [3, 4])
    copy_obj = safe_deepcopy(original)
    assert copy_obj == original
    assert copy_obj is not original
    assert copy_obj[2] is not original[2]


def test_deepcopy_with_frozenset():
    original = frozenset([1, 2, 3, (4, 5)])
    copy_obj = safe_deepcopy(original)
    assert copy_obj == original
    assert copy_obj is not original


def test_deepcopy_with_object():
    original = NormalObject(10)
    copy_obj = safe_deepcopy(original)
    assert copy_obj.value == original.value
    assert copy_obj is not original
    assert copy_obj.nested is not original.nested


def test_deepcopy_with_custom_deepcopy_fallback():
    original = {"origin": NormalObject(10)}
    copy_obj = safe_deepcopy(original)
    assert copy_obj is not original
    assert copy_obj["origin"].value == original["origin"].value


def test_shallow_copy_fallback():
    original = {"origin": NonDeepcopyable(10)}
    copy_obj = safe_deepcopy(original)
    assert copy_obj is not original
    assert copy_obj["origin"].value == original["origin"].value


def test_circular_reference():
    original = []
    original.append(original)
    copy_obj = safe_deepcopy(original)
    assert copy_obj is not original
    assert copy_obj[0] is copy_obj


def test_memoization():
    original = {"a": 1, "b": 2}
    memo = {}
    copy_obj = safe_deepcopy(original, memo)
    assert copy_obj is memo[id(original)]


def test_deepcopy_object_without_dict():
    original = {"origin": WithoutDict(10)}
    copy_obj = safe_deepcopy(original)
    assert copy_obj["origin"].value == original["origin"].value
    assert copy_obj is not original
    assert copy_obj["origin"] is original["origin"]
    assert (
        hasattr(copy_obj["origin"], "__dict__") is False
    )  # Ensure __dict__ is not present

    original = [WithoutDict(10)]
    copy_obj = safe_deepcopy(original)
    assert copy_obj[0].value == original[0].value
    assert copy_obj is not original
    assert copy_obj[0] is original[0]

    original = (WithoutDict(10),)
    copy_obj = safe_deepcopy(original)
    assert copy_obj[0].value == original[0].value
    assert copy_obj is not original
    assert copy_obj[0] is original[0]

    original_item = WithoutDict(10)
    original = set([original_item])
    copy_obj = safe_deepcopy(original)
    assert copy_obj is not original
    copy_obj_item = copy_obj.pop()
    assert copy_obj_item.value == original_item.value
    assert copy_obj_item is original_item

    original_item = WithoutDict(10)
    original = frozenset([original_item])
    copy_obj = safe_deepcopy(original)
    assert copy_obj is not original
    copy_obj_item = list(copy_obj)[0]
    assert copy_obj_item.value == original_item.value
    assert copy_obj_item is original_item

def test_memo():
    obj = NormalObject(10)
    original = {"origin": obj}
    memo = {id(original):obj}
    copy_obj = safe_deepcopy(original, memo)
    assert copy_obj is memo[id(original)]

def test_unhandled_type():
    original = {"origin": NonCopyableObject(10)}
    copy_obj = safe_deepcopy(original)
    assert copy_obj["origin"].value == original["origin"].value
    assert copy_obj is not original
    assert copy_obj["origin"] is original["origin"]
    assert hasattr(copy_obj, "__dict__") is False  # Ensure __dict__ is not present
