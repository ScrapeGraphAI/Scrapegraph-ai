""" 
Module for making the request on the web
"""
import requests


def search_word_on_google(word):
    """ 
    Function that given a word it finds it on the intenet
    """
    url = f"https://www.google.com/search?q={word}"
    headers = {
        'User-Agent': """Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (
            KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"""
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print("Search request successful!")
        # You can parse the HTML response using BeautifulSoup or other libraries
        print("Response content:")
        print(response.text)
    else:
        print(
            f"Failed to make search request. Status code: {response.status_code}")

# Example usage
