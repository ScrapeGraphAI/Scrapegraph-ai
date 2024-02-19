""" 
Basic example of scraping pipeline using SmartScraper
"""

import os
from dotenv import load_dotenv
from scrapegraphai.models import OpenAIImageToText, OpenAITextToSpeech
from scrapegraphai.utils import save_audio_from_bytes

load_dotenv()

# Define the configuration for the language model
openai_key = os.getenv("OPENAI_APIKEY")
llm_config = {
    "api_key": openai_key,
    "model_name": "gpt-4-vision-preview",
}

model = OpenAIImageToText(llm_config)
answer = model.run("https://raw.githubusercontent.com/VinciGit00/Scrapegraph-ai/main/docs/assets/scrapegraphai_logo.png")
print(answer)

text_to_speech = OpenAITextToSpeech(llm_config, model="tts-1", voice="alloy")

text = "Today is a wonderful day to build something people love!"
audio = text_to_speech.run(text)

# Save the audio to a file
curr_dir = os.path.dirname(os.path.realpath(__file__))
file_path = os.path.join(curr_dir, "text2speech.mp3")

save_audio_from_bytes(audio, file_path)

print(f"Speech file saved to: {file_path}")