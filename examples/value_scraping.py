"""
Example of scraping using just a link
 """
import os
from dotenv import load_dotenv
from scrapegraphai import _get_function, send_request

load_dotenv()


def main():
    """ """
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

    selected_model = "gpt-3.5-turbo"
    temperature_value = 0.7

    mockup_world_url = "https://sport.sky.it/nba?gr=www"

    result = send_request(openai_key, _get_function(
        mockup_world_url), request_settings, selected_model, temperature_value, 'cl100k_base')

    print("Result:", result)


if __name__ == "__main__":
    main()
