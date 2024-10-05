"""
This utility function extracts the code from a given string.
"""
import re

def extract_code(code: str) -> str:
    """
    Module for extracting code 
    """
    pattern = r'```(?:python)?\n(.*?)```'

    match = re.search(pattern, code, re.DOTALL)

    return match.group(1) if match else code
