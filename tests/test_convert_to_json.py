""" 
Module for testing convert_to_json inside the folder yosoai/convert_to_json.py
"""
import unittest
from yosoai.convert_to_json import convert_to_json


class TestConvertToJSonFunction(unittest.TestCase):
    """ 
    class for testing convert_to_json inside the folder yosoai/convert_to_json.py
    """

    def test_get_json(self):
        """
        function for testing convert_to_json inside the folder yosoai/convert_to_json.py
        """
        example = {"trial": [1, 2, 3]}
        filename = "result"
        path = "../YOSO-ai/tests"
        convert_to_json(example, filename, path)
