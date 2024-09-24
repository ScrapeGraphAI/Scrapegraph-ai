"""
This utility function saves the byte response as an audio file.
"""
from pathlib import Path
from typing import Union

def save_audio_from_bytes(byte_response: bytes, output_path: Union[str, Path]) -> None:
    """
    Saves the byte response as an audio file to the specified path.

    Args:
        byte_response (bytes): The byte array containing audio data.
        output_path (Union[str, Path]): The destination 
        file path where the audio file will be saved.

    Example:
        >>> save_audio_from_bytes(b'audio data', 'path/to/audio.mp3')

    This function writes the byte array containing audio data to a file, saving it as an audio file.
    """

    if not isinstance(output_path, Path):
        output_path = Path(output_path)

    with open(output_path, 'wb') as audio_file:
        audio_file.write(byte_response)
