"""
parse_response_to_dict module
"""
import re
import json

def parse_response_to_dict(response_text: str) -> dict:
    """
    Parse the response text to a dictionary, handling different formats.

    Args:
        response_text (str): The raw text response from the model.

    Returns:
        dict: The parsed dictionary.
    """
    # Regex to capture text between ```json and ```
    json_pattern = r'```json\s*(.*?)\s*```'

    # Check if response matches the pattern
    match = re.search(json_pattern, response_text, re.DOTALL)
    if match:
        json_str = match.group(1)
    else:
        # If no match, consider the whole response as potential JSON
        json_str = response_text

    # Clean any common escape characters and whitespace issues
    cleaned_json_str = json_str.replace('\\n', '').replace('\\', '').strip()

    # Parse the cleaned string into a dictionary
    try:
        parsed_dict = json.loads(cleaned_json_str)
    except json.JSONDecodeError:
        raise ValueError("The response could not be parsed into a valid JSON dictionary.")

    return parsed_dict
