"""
Module for removing the unused html tags
"""


def remover(file: str, only_body: bool = False) -> str:
    """
    This function elaborates the HTML file and remove all the not necessary tag

    Parameters:
        file (str): the file to parse

    Returns:
        str: the parsed file
    """

    res = ""

    if only_body:
        is_body = True
    else:
        is_body = False

    for elem in file.splitlines():
        if "<title>" in elem:
            res = res + elem

        if "<body>" in elem:
            is_body = True

        if "</body>" in elem:
            break

        if "<script>" in elem:
            continue

        if is_body:
            res = res + elem

    return res.replace("\\n", "")
