"""
Module for rotating proxies
"""
from fp.fp import FreeProxy


def proxy_generator(num_ips: int) -> list:
    """
    Generates a specified number of proxy IP addresses using the FreeProxy library.

    Args:
        num_ips (int): The number of proxy IPs to generate and rotate through.

    Returns:
        list: A list of proxy IP addresses.

    Example:
        >>> proxy_generator(5)
        [
            '192.168.1.1:8080',
            '103.10.63.135:8080',
            '176.9.75.42:8080',
            '37.57.216.2:8080',
            '113.20.31.250:8080'
        ]

    This function fetches fresh proxies and indexes them, making it easy to manage multiple proxy configurations.
    """

    res = []

    for i in range(0, num_ips):
        res.append(FreeProxy().get())
    return res
