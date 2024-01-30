from utils.class_generator import Generator

from utils.getter import get_function, scraper

values = [
    {
        "title": "title",
        "type": "str",
        "description": "Title of the items"
    }
]

if __name__ == "__main__":

    generator_instance = Generator(values, 0, "gpt-3.5-turbo")

    res = generator_instance.invocation(scraper("https://www.mockupworld.co", 4197))
    
    print(res)