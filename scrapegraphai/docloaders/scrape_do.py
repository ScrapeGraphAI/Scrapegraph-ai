"""
Scrape_do module
"""
import urllib.parse
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def scrape_do_fetch(token, target_url, use_proxy=False, geoCode=None, super_proxy=False):
    """
    Fetches the IP address of the machine associated with the given URL using Scrape.do.

    Args:
        token (str): The API token for Scrape.do service.
        target_url (str): A valid web page URL to fetch its associated IP address.
        use_proxy (bool): Whether to use Scrape.do proxy mode. Default is False.
        geoCode (str, optional): Specify the country code for 
        geolocation-based proxies. Default is None.
        super_proxy (bool): If True, use Residential & Mobile Proxy Networks. Default is False.

    Returns:
        str: The raw response from the target URL.
    """
    encoded_url = urllib.parse.quote(target_url)
    if use_proxy:
        # Create proxy mode URL
        proxyModeUrl = f"http://{token}:@proxy.scrape.do:8080"
        proxies = {
            "http": proxyModeUrl,
            "https": proxyModeUrl,
        }
        # Add optional geoCode and super proxy parameters if provided
        params = {"geoCode": geoCode, "super": str(super_proxy).lower()} if geoCode else {}
        response = requests.get(target_url, proxies=proxies, verify=False, params=params)
    else:
        # API Mode URL
        url = f"http://api.scrape.do?token={token}&url={encoded_url}"
        response = requests.get(url)

    return response.text
