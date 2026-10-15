"""
Module for refusing scrape targets that point at cloud metadata endpoints
"""

import ipaddress
import socket
from urllib.parse import urljoin, urlparse

# Metadata services that sit outside the link-local ranges
_METADATA_ADDRESSES = {
    ipaddress.ip_address("fd00:ec2::254"),
    ipaddress.ip_address("100.100.100.200"),
}


def validate_url(url: str) -> None:
    """
    Raises ValueError if the host of the url resolves to a link-local address
    (169.254.0.0/16, fe80::/10) or to a known cloud metadata address.
    Hosts that do not resolve are left to fail when they are fetched.

    Args:
        url (str): The url about to be fetched.

    Raises:
        ValueError: If any address the host resolves to is not allowed.
    """
    hostname = urlparse(url).hostname
    if not hostname:
        return

    try:
        # urllib3 drops an IPv6 zone id (fe80::1%25eth0) before connecting
        infos = socket.getaddrinfo(hostname.split("%")[0], None)
    except socket.gaierror:
        return

    for info in infos:
        address = ipaddress.ip_address(info[4][0].split("%")[0])
        if isinstance(address, ipaddress.IPv6Address) and address.ipv4_mapped:
            address = address.ipv4_mapped
        if address.is_link_local or address in _METADATA_ADDRESSES:
            raise ValueError(
                "The url points to a link-local or cloud metadata address "
                "and will not be fetched."
            )


def validate_redirect(response, **kwargs) -> None:
    """
    Response hook for requests that checks the target of a redirect before
    requests follows it.

    Args:
        response: The response that was just received.

    Raises:
        ValueError: If the redirect target is not allowed.
    """
    if response.is_redirect:
        validate_url(urljoin(response.url, response.headers["location"]))
