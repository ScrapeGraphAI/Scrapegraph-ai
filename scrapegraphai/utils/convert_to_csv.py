"""
Module that given a filename and a position saves the file in the csv format
"""
import os
import sys
import pandas as pd

def convert_to_csv(data: dict, filename: str, position: str = None) -> None:
    """
    Converts a dictionary to a CSV file and saves it at a specified location.

    Args:
        data (dict): The data to be converted into CSV format.
        filename (str): The name of the output CSV file, without the '.csv' extension.
        position (str, optional): The file path where the CSV should be saved. Defaults to the directory of the caller script if not provided.

    Returns:
        None: The function does not return anything.
        
    Raises:
        FileNotFoundError: If the specified directory does not exist.
        PermissionError: If write permissions are lacking for the directory.
        TypeError: If `data` is not a dictionary.
        Exception: For other issues that may arise during the creation or saving of the CSV file.

    Example:
        >>> convert_to_csv({'id': [1, 2], 'value': [10, 20]}, 'output', '/path/to/save')
        Saves a CSV file named 'output.csv' at '/path/to/save'.
    """

    if ".csv" in filename:
        filename = filename.replace(".csv", "")

    if position is None:
        caller_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        position = caller_dir

    try:
        if not isinstance(data, dict):
            raise TypeError("Input data must be a dictionary")

        os.makedirs(position, exist_ok=True)

        df = pd.DataFrame.from_dict(data, orient='index')
        df.to_csv(os.path.join(position, f"{filename}.csv"), index=False)

    except FileNotFoundError as fnfe:
        raise FileNotFoundError(
            f"The specified directory '{position}' does not exist.") from fnfe
    except PermissionError as pe:
        raise PermissionError(
            f"You don't have permission to write to '{position}'.") from pe
    except Exception as e:
        raise e
