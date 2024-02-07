# 🤖 YOSO-ai: You Only Scrape Once

YOSO-ai is a Python **Open Source** library that uses LLM and Langchain for faster and efficient web scraping. Just say which information you want to extract and the library will do it for you.

Official documentation page: [yoso-ai.readthedocs.io](https://yoso-ai.readthedocs.io/)

# 🔍 Demo

Try out YOSO-ai in your browser:

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/VinciGit00/YOSO-ai)

# 🔧 Quick Setup

Follow the following steps:

1.

```bash
git clone https://github.com/VinciGit00/yoso-ai.git
```

2.  (Optional)

```bash
python -m venv venv
source ./venv/bin/activate
```

3.  ```bash
    pip install -r requirements.txt
    # if you want to install it as a library
    pip install .

    # or if you plan on developing new features it is best to also install the extra dependencies using

    pip install -r requirements-dev.txt
    # if you want to install it as a library
    pip install .[dev]
    ```

4.  Create your personal OpenAI API key from [here](https://platform.openai.com/api-keys)
5.  (Optional) Create a .env file inside the main and paste the API key

```config
API_KEY="your openai.com api key"
```

6. You are ready to go! 🚀
7. Try running the examples using:

```bash
python -m examples.html_scraping
# or if you are outside of the project folder
python -m yoso-ai.examples.html_scraping
```

# 📖 Examples

```python
import os
from dotenv import load_dotenv
from yosoai import get_function, send_request

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
```

### Case 2: Passing your own HTML code

```python
import os
from dotenv import load_dotenv
from yosoai import send_request

load_dotenv()

# Example using a HTML code
query_info = '''
        Given this code extract all the information in a json format about the news.

        <article class="c-card__wrapper aem_card_check_wrapper" data-cardindex="0">
            <div class="c-card__content">
                <h2 class="c-card__title">Booker show with 52 points, whoever has the most games over 50</h2>
                <div class="c-card__label-wrapper c-label-wrapper">
                    <span class="c-label c-label--article-heading">Standings</span>
                </div>
                <p class="c-card__abstract">The Suns' No. 1 dominated the match won in New Orleans, scoring 52 points. It's about...</p>
                <div class="c-card__info">
                    <time class="c-card__date" datetime="20 gen - 07:54">20 gen - 07:54</time>
                ...
                </div>
            </div>
            <div class="c-card__img-wrapper">
                <figure class="o-aspect-ratio o-aspect-ratio--16-10 ">
                    <img crossorigin="anonymous" class="c-card__img j-lazyload" alt="Partite con 50+ punti: Booker in Top-20" data-srcset="..." sizes="..." loading="lazy" data-src="...">
                    <noscript>
                        <img crossorigin="anonymous" class="c-card__img" alt="Partite con 50+ punti: Booker in Top-20" srcset="..." sizes="..." src="...">
                    </noscript>
                </figure>
                <i class="icon icon--media icon--gallery icon--medium icon--c-primary">
                </i>
            </div>
        </article>
    '''
def main():
    # Get OpenAI API key from environment variables
    openai_key = os.getenv("API_KEY")
    if not openai_key:
        print("Error: OpenAI API key not found in environment variables.")
        return

    # Example values for the request
    request_settings = [
        {
            "title": "title",
            "type": "str",
            "description": "Title of the news"
        }
    ]

    # Choose the desired model and other parameters
    selected_model = "gpt-3.5-turbo"
    temperature_value = 0.7

    # Invoke send_request function
    result = send_request(openai_key, query_info, request_settings, selected_model, temperature_value, 'cl100k_base')

    # Print or process the result as needed
    print("Result:", result)

if __name__ == "__main__":
    main()
```

Note: all the model are available at the following link: [https://platform.openai.com/docs/models](https://platform.openai.com/docs/models), be sure you have enabled that keys

# Example of output

Given the following input

```python
    [
        {
            "title": "title",
            "type": "str",
            "description": "Title of the news"
        }
    ]

```

using as a input the website [https://sport.sky.it/nba?gr=www](https://sport.sky.it/nba?gr=www)

The oputput format is a dict and its the following:

```bash
    {
    'title': 'Booker show with 52 points, whoever has the most games over 50'
    }
```

# Developed by

<p align="center">
  <a href="https://vincigit00.github.io/">
    <img src="docs/assets/logo_vincios.png" alt="Vincios Logo" style="width: 30%;">
  </a>
  <a href="https://lurenss.github.io/">
    <img src="docs/assets/logo_lurens.png" alt="Lurenss Logo" style="width: 30%;">
  </a>
  <a href="https://perinim.github.io/">
    <img src="docs/assets/logo_perinilab.png" alt="PeriniLab Logo" style="width: 30%;">
  </a>
</p>
