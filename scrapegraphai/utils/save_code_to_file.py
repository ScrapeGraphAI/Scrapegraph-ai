"""
save_code_to_file module
"""

def save_code_to_file(code: str, filename:str) -> None:
    """
    Saves the generated code to a Python file.

    Args:
        code (str): The generated code to be saved.
        filename (str): name of the output file
    """
    with open(filename, "w") as file:
        file.write(code)
