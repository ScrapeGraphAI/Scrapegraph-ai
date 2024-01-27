import requests
from bs4 import BeautifulSoup


HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
'Accept-Language': 'en-US'}


def get_function(link:str, param = HEADERS) -> str:
    """
    It sends a GET request to the specified link with optional headers.

    Parameters:
    link (str): The URL to send the GET request to.
    param (dict): Optional headers to include in the request. Default is HEADERS.

    Returns:
    str: The content of the response as a string.
    """
    response = requests.get(url=link, headers=HEADERS)
    return str(response.content)




def scraper(link: str, max_char: int) -> str:
    """
    Scrapes the HTML text and removes unwanted elements, text, and comments.

    Args:
        link (str): The HTML link to be scraped.
        max_char (int): The maximum number of characters in the returned HTML body.

    Returns:
        str: The scraped HTML body as a string without script meta tags and limited to max_char characters.
    """
    text = get_function(link)
    soup = BeautifulSoup(text, 'html.parser')

    unwanted_elements = ['head', 'script', 'style']
    unwanted_text = "Per discutere l'accesso automatizzato ai dati di Amazon"
    unwanted_comment = "Correios.DoNotSend"

    for element in soup(unwanted_elements):
        element.decompose()

    for unwanted_content in soup.find_all(string=lambda text: unwanted_text in text or unwanted_comment in text):
        unwanted_content.extract()

    html_body = str(soup.body).replace('\n', '')

    # Limit the number of characters in the HTML body
    return html_body[:max_char]
