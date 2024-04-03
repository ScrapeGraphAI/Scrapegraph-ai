"""
This utility function saves the byte response as an audio file.
"""
from pathlib import Path
from typing import Union


def save_audio_from_bytes(byte_response: bytes, output_path: Union[str, Path]) -> None:
    """
    Saves the byte response as an audio file.

    Args:
        byte_response (bytes): The byte response containing the generated speech.
        output_path (str or Path): The file path where the generated speech should be saved.
    """
    if not isinstance(output_path, Path):
        output_path = Path(output_path)

    with open(output_path, 'wb') as audio_file:
        audio_file.write(byte_response)
