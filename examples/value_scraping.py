import os
from dotenv import load_dotenv
from yosoai.getter import get_function
from yosoai.request import send_request

load_dotenv()

def main():
    # Get OpenAI API key from environment variables
    openai_key = os.getenv("API_KEY")
    if not openai_key:
        print("Error: OpenAI API key not found in environment variables.")
        return

    # Example values for the request
    request_settings = [
        {
        "title": "title_news",
        "type": "str",
        "description": "Give me the name of the news"
        }
    ]

    # Choose the desired model and other parameters
    selected_model = "gpt-3.5-turbo"
    temperature_value = 0.7

    # Mockup World URL
    mockup_world_url = "https://sport.sky.it/nba?gr=www"

    # Invoke send_request function
    result = send_request(openai_key, get_function(mockup_world_url), request_settings, selected_model, temperature_value, 'cl100k_base')

    # Print or process the result as needed
    print("Result:", result)

if __name__ == "__main__":
    main()