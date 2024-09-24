import copy
import pytest

# Assuming the custom_deepcopy function is imported or defined above this line
from scrapegraphai.utils.copy import DeepCopyError, safe_deepcopy
from pydantic.v1 import BaseModel

class PydantObject(BaseModel):
    value: int

class NormalObject:
    def __init__(self, value):
        self.value = value
        self.nested = [1, 2, 3]


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

def test_unhandled_type():
    with pytest.raises(DeepCopyError):
        original = {"origin": NonCopyableObject(10)}
        copy_obj = safe_deepcopy(original)

def test_client():
    llm_instance_config = {
        "model": "moonshot-v1-8k",
        "base_url": "https://api.moonshot.cn/v1",
        "moonshot_api_key": "xxx",
    }

    from langchain_community.chat_models.moonshot import MoonshotChat

    llm_model_instance = MoonshotChat(**llm_instance_config)
    copy_obj = safe_deepcopy(llm_model_instance)
    
    assert copy_obj
    assert hasattr(copy_obj, 'callbacks')

def test_circular_reference_in_dict():
    original = {}
    original['self'] = original  # Create a circular reference
    copy_obj = safe_deepcopy(original)
    
    # Check that the copy is a different object
    assert copy_obj is not original
    # Check that the circular reference is maintained in the copy
    assert copy_obj['self'] is copy_obj

def test_with_pydantic():
    original = PydantObject(value=1)
    copy_obj = safe_deepcopy(original)
    assert copy_obj.value == original.value
    assert copy_obj is not original 

def test_with_boto3():
    import boto3
    boto_client = boto3.client("bedrock-runtime", region_name="us-west-2")
    copy_obj = safe_deepcopy(boto_client)
    assert copy_obj == boto_client