""" 
Test file for the class save_audio_from_bytes
"""
import unittest
import os
from tempfile import TemporaryDirectory
from pathlib import Path
from scrapegraphai.utils.save_audio_from_bytes import save_audio_from_bytes


class TestSaveAudioFromBytes(unittest.TestCase):
    """ 
    Test class
    """

    def test_save_audio_from_bytes(self):
        """ 
        First test
        """
        with TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)

            byte_response = b'\x12\x34\x56\x78\x90'

            output_path = temp_dir_path / "generated_speech.wav"

            save_audio_from_bytes(byte_response, output_path)

            self.assertTrue(output_path.exists())

            self.assertTrue(os.path.getsize(output_path) > 0)


if __name__ == "__main__":
    unittest.main()
