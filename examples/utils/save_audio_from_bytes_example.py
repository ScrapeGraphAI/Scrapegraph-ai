""" 
Example for th e file save_audio_from_bytes
"""
from scrapegraphai.utils.save_audio_from_bytes import save_audio_from_bytes

BYTE_RESPONSE = b'\x12\x34\x56\x78\x90'

OUTPUT_PATH = "generated_speech.wav"

save_audio_from_bytes(BYTE_RESPONSE, OUTPUT_PATH)
