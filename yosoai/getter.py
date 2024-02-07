import requests

HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
           'Accept-Language': 'en-US'}

def get_function(link:str, param = HEADERS) -> str:
    """
    It sends a GET request to the specified link with optional headers.

    Args:
        link (str): The URL to send the GET request to.
        param (dict): Optional headers to include in the request. Default is HEADERS.

    Returns:
        str: The content of the response as a string.
    """
    response = requests.get(url=link, headers=param)
    return str(response.content)

def remover(file:str) -> str:
    """
    This function elaborates the HTML file and remove all the not necessary tag
    
    Parameters:
        file (str): the file to parse

    Returns:
        str: the parsed file
    """

    res = ""
    
    isBody = False

    for elem in file.splitlines():
        if "<title>" in elem:
            res = res + elem

        if "<body>" in elem: 
            isBody = True

        if "</body>" in elem:
            break

        if "<script>" in elem:
            continue

        if isBody == True:
            res = res + elem

    return res.replace("\n", "")