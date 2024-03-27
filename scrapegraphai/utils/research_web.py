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
        'User-Agent': """ Mozilla/5.0 (Windows NT 10.0; Win64; x64) A
        ppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"""
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
    except requests.RequestException as e:
        print(f"Error occurred: {e}")
        return

    if response.status_code == 200:
        print("Search request successful!")
        # You can parse the HTML response using BeautifulSoup or other libraries
        print("Response content:")
        print(response.text)
    else:
        print(
            f"Failed to make search request. Status code: {response.status_code}")
