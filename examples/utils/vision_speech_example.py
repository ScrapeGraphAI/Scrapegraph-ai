""" 
Basic example of scraping pipeline using SmartScraper
"""

import os
from dotenv import load_dotenv
from scrapegraphai.models import OpenAIImageToText, OpenAITextToSpeech
from scrapegraphai.utils import save_audio_from_bytes

load_dotenv()
openai_key = os.getenv("OPENAI_APIKEY")

# Define the configuration for the graph
config = {
    "itt_model": {
        "api_key": openai_key,
        "model": "gpt-4-vision-preview",
    },
    "tts_model": {
        "api_key": openai_key,
        "model": "tts-1",
        "voice": "alloy"
    },
}

itt_model = OpenAIImageToText(config["itt_model"])
img_to_text_result = itt_model.run(
    "https://raw.githubusercontent.com/VinciGit00/Scrapegraph-ai/main/docs/assets/scrapegraphai_logo.png"
    )

print(f"Image description: {img_to_text_result}")

tts_model = OpenAITextToSpeech(config["tts_model"])

audio = tts_model.run(
    img_to_text_result
    )

# Save the audio to a file
file_name = "image_description.mp3"
curr_dir = os.path.dirname(os.path.realpath(__file__))
output_path = os.path.join(curr_dir, file_name)

save_audio_from_bytes(audio, output_path)

print(f"Audio file saved to: {output_path}")
