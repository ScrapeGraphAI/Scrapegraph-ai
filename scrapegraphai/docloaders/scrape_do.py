"""
scrape_do module
"""
import urllib.parse
import requests

def scrape_do_fetch(token, target_url):
    """
    This function takes a token and a URL as inputs. 
    It returns the IP address of the machine associated with the given URL.

    Args:
        token (str): The API token for scrape.do service.
        target_url (str): A valid web page URL to fetch its associated IP address.

    Returns:
        str: The IP address of the machine associated with the target URL.
    """

    encoded_url = urllib.parse.quote(target_url)
    url = f"http://api.scrape.do?token={token}&url={encoded_url}"
    response = requests.request("GET", url)
    return response.text
