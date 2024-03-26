"""
Module that given a filename and a position saves the file in the csv format
"""
import os
import sys
import pandas as pd


def convert_to_csv(data: dict, filename: str, position: str = None):
    """
    Converts a dictionary to a CSV file and saves it.

    Args:
    data (dict): Data to be converted to CSV.
    filename (str): Name of the CSV file (without the .csv extension).
    position (str): Optional path where the file should be saved. If not provided,
    the directory of the caller script will be used.

    Raises:
    ValueError: If the filename contains '.csv'.
    FileNotFoundError: If the specified directory does not exist.
    PermissionError: If the program lacks write permission for the directory.
    TypeError: If the input data is not a dictionary.
    Exception: For other potential errors during DataFrame creation or CSV saving.
    """

    if ".csv" in filename:
        raise ValueError("The filename should not contain '.csv'")

    # Get the directory of the caller script if position is not provided
    if position is None:
        caller_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        position = caller_dir

    try:
        if not isinstance(data, dict):
            raise TypeError("Input data must be a dictionary")

        os.makedirs(position, exist_ok=True)  # Create directory if needed

        df = pd.DataFrame.from_dict(data, orient='index')
        df.to_csv(os.path.join(position, f"{filename}.csv"), index=False)

    except FileNotFoundError as fnfe:
        raise FileNotFoundError(
            f"The specified directory '{position}' does not exist.") from fnfe
    except PermissionError as pe:
        raise PermissionError(
            f"You don't have permission to write to '{position}'.") from pe
    except Exception as e:
        raise e  # Re-raise other potential errors
