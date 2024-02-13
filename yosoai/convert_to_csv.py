"""
Module that given a filename and a position saves the file in the csv format
"""
import os
import pandas as pd


def convert_to_csv(data: dict, filename: str, position: str):
    """
    Convert data to JSON format and save it to a file.

    Args:
        data (dict): Data to save.
        filename (str): Name of the file to save without .csv extension.
        position (str): Directory where the file should be saved.

    Raises:
        ValueError: If filename contains '.csv'.
        FileNotFoundError: If the specified directory does not exist.
        PermissionError: If the program does not have permission to write to the directory.
    """
    if ".csv" in filename:
        raise ValueError("The filename should not contain '.csv'")

    try:
        os.makedirs(position, exist_ok=True)
        pd.DataFrame.from_dict(data, orient='index').to_csv(
            os.path.join(position, f"{filename}.csv"), index=False)
    except FileNotFoundError as fnfe:
        raise FileNotFoundError(
            f"The specified directory '{position}' does not exist.") from fnfe
    except PermissionError as pe:
        raise PermissionError(
            f"You don't have permission to write to '{position}'.") from pe
    except Exception as e:
        raise e
