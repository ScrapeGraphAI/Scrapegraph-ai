"""
Module for rotating proxies
"""
from fp.fp import FreeProxy


def proxy_generator(num_ips: int):
    """
    Rotates through a specified number of proxy IPs using the FreeProxy library.

    Args:
        num_ips (int): The number of proxy IPs to rotate through.

    Returns:
        dict: A dictionary containing the rotated proxy IPs, indexed by their position in rotation.

    Example:
        >>> proxy_generator(5)
        {
            0: '192.168.1.1:8080',
            1: '103.10.63.135:8080',
            2: '176.9.75.42:8080',
            3: '37.57.216.2:8080',
            4: '113.20.31.250:8080'
        }
    """
    res = []

    for i in range(0, num_ips):
        res.append(FreeProxy().get())
    return res
