"""
Example of using convert_to_json function to save data in JSON format.
"""
import os
from scrapegraphai.utils.convert_to_json import convert_to_json

# Data to save in JSON format
data_to_save = {
    "name": "John Doe",
    "age": 30,
    "city": "New York"
}

FILENAME = "example_data"
DIRECTORY = "data_output"

try:
    convert_to_json(data_to_save, FILENAME, DIRECTORY)
    print(
        f"Data has been successfully saved to {os.path.join(DIRECTORY, FILENAME)}.json")
except ValueError as value_error:
    print(value_error)
except FileNotFoundError as file_not_found_error:
    print(file_not_found_error)
except PermissionError as permission_error:
    print(permission_error)
except Exception as exception:
    print(f"An error occurred: {exception}")
