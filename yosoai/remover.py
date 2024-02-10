def remover(file:str, only_body:bool = False) -> str:
    """
    This function elaborates the HTML file and remove all the not necessary tag
    
    Parameters:
        file (str): the file to parse

    Returns:
        str: the parsed file
    """

    res = ""
    
    if only_body == True:
        isBody = True
    else:
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

    return res.replace("\\n", "")