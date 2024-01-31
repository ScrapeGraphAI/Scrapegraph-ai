import os
from dotenv import load_dotenv
from utils.getter import scraper
from utils.class_generator import Generator

load_dotenv()

MY_ENV_VAR = os.getenv('API_KEY')

values = [
    {
        "title": "title_website",
        "type": "str",
        "description": "Give me the website name"
    }
]

if __name__ == "__main__":

    generator_instance = Generator(values, MY_ENV_VAR, 0, "gpt-3.5-turbo")

    res = generator_instance.invocation(scraper("https://www.mockupworld.co", 4197))
    
    print(res)