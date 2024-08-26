"""
Convert to json module
"""
import json
import os
import sys

def convert_to_json(data: dict, filename: str, position: str = None) -> None:
    """
    Converts a dictionary to a JSON file and saves it at a specified location.

    Args:
        data (dict): The data to be converted into JSON format.
        filename (str): The name of the output JSON file, without the '.json' extension.
        position (str, optional): The file path where the JSON file should be saved. 
        Defaults to the directory of the caller script if not provided.

    Returns:
        None: The function does not return anything.
        
    Raises:
        ValueError: If 'filename' contains '.json'.
        FileNotFoundError: If the specified directory does not exist.
        PermissionError: If write permissions are lacking for the directory.

    Example:
        >>> convert_to_json({'id': [1, 2], 'value': [10, 20]}, 'output', '/path/to/save')
        Saves a JSON file named 'output.json' at '/path/to/save'.

    Notes:
        This function automatically ensures the directory exists before 
        attempting to write the file. 
        If the directory does not exist, it will attempt to create it.
    """

    if ".json" in filename:
        filename = filename.replace(".json", "")  # Remove .json extension

    if position is None:
        caller_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        position = caller_dir

    try:
        os.makedirs(position, exist_ok=True)
        with open(os.path.join(position, f"{filename}.json"), "w", encoding="utf-8") as f:
            f.write(json.dumps(data))
    except FileNotFoundError as fnfe:
        raise FileNotFoundError(
            f"The specified directory '{position}' does not exist.") from fnfe
    except PermissionError as pe:
        raise PermissionError(
            f"You don't have permission to write to '{position}'.") from pe
