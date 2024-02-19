""" 
Teest for convert_to_csv
"""
import os
from scrapegraphai.utils.convert_to_csv import convert_to_csv


def main():
    """
    Example usage of the convert_to_csv function.
    """
    # Example data
    data = {
        'Name': ['John', 'Alice', 'Bob'],
        'Age': [30, 25, 35],
        'City': ['New York', 'San Francisco', 'Seattle']
    }

    # Example filename and position
    filename = "example_data"
    position = "./output"

    try:
        # Convert data to CSV and save
        convert_to_csv(data, filename, position)
        print(
            f"Data saved successfully to {os.path.join(position, filename)}.csv")
    except ValueError as ve:
        print(f"ValueError: {ve}")
    except FileNotFoundError as fnfe:
        print(f"FileNotFoundError: {fnfe}")
    except PermissionError as pe:
        print(f"PermissionError: {pe}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
