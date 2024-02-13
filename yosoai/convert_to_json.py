"""
Module that given a filename and a position saves the file in the json format
"""
import json
import os


def convert_to_json(data: dict, filename: str, position: str):
    """
    Convert data to CSV format and save it to a file.

    Args:
        data (dict): Data to save.
        filename (str): Name of the file to save without .json extension.
        position (str): Directory where the file should be saved.

    Raises:
        ValueError: If filename contains '.json'.
        FileNotFoundError: If the specified directory does not exist.
        PermissionError: If the program does not have permission to write to the directory.
    """
    if ".json" in filename:
        raise ValueError("The filename should not contain '.json'")

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
    except Exception as e:
        raise e
