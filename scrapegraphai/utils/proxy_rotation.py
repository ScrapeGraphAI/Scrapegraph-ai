"""
Module for rotating proxies
"""

import ipaddress
import random
import re
from typing import List, Optional, Set, TypedDict
from urllib.parse import urlparse

import requests
from fp.errors import FreeProxyException
from fp.fp import FreeProxy


class ProxyBrokerCriteria(TypedDict, total=False):
    """
    proxy broker criteria
    """

    anonymous: bool
    countryset: Set[str]
    secure: bool
    timeout: float
    search_outside_if_empty: bool


class ProxySettings(TypedDict, total=False):
    """
    proxy settings
    """

    server: str
    bypass: str
    username: str
    password: str


class Proxy(ProxySettings):
    """
    proxy server information
    """

    criteria: ProxyBrokerCriteria


def search_proxy_servers(
    anonymous: bool = True,
    countryset: Optional[Set[str]] = None,
    secure: bool = False,
    timeout: float = 5.0,
    max_shape: int = 5,
    search_outside_if_empty: bool = True,
) -> List[str]:
    """search for proxy servers that match the specified broker criteria

    Args:
        anonymous: whether proxy servers should have minimum level-1 anonymity.
        countryset: admissible proxy servers locations.
        secure: whether proxy servers should support HTTP or HTTPS; defaults to HTTP;
        timeout: The maximum timeout for proxy responses; defaults to 5.0 seconds.
        max_shape: The maximum number of proxy servers to return; defaults to 5.
        search_outside_if_empty: whether countryset should be extended if empty.

    Returns:
        A list of proxy server URLs matching the criteria.

    Example:
        >>> search_proxy_servers(
        ...     anonymous=True,
        ...     countryset={"GB", "US"},
        ...     secure=True,
        ...     timeout=1.0
        ...     max_shape=2
        ... )
        [
            "http://103.10.63.135:8080",
            "http://113.20.31.250:8080",
        ]
    """
    proxybroker = FreeProxy(
        anonym=anonymous,
        country_id=countryset,
        elite=True,
        https=secure,
        timeout=timeout,
    )

    def search_all(proxybroker: FreeProxy, k: int, search_outside: bool) -> List[str]:
        candidateset = proxybroker.get_proxy_list(search_outside)
        random.shuffle(candidateset)

        positive = set()

        for address in candidateset:
            setting = {proxybroker.schema: f"http://{address}"}

            try:
                server = proxybroker._FreeProxy__check_if_proxy_is_working(setting)

                if not server:
                    continue

                positive.add(server)

                if len(positive) < k:
                    continue

                return list(positive)

            except requests.exceptions.RequestException:
                continue

        n = len(positive)

        if n < k and search_outside:
            proxybroker.country_id = None

            try:
                negative = set(search_all(proxybroker, k - n, False))
            except FreeProxyException:
                negative = set()

            positive = positive | negative

        if not positive:
            raise FreeProxyException("missing proxy servers for criteria")

        return list(positive)

    return search_all(proxybroker, max_shape, search_outside_if_empty)


def _parse_proxy(proxy: ProxySettings) -> ProxySettings:
    """parses a proxy configuration with known server

    Args:
        proxy: The proxy configuration to parse.

    Returns:
        A 'playwright' compliant proxy configuration.
    """
    assert "server" in proxy, "missing server in the proxy configuration"

    auhtorization = [x in proxy for x in ("username", "password")]

    message = "username and password must be provided in pairs or not at all"

    assert all(auhtorization) or not any(auhtorization), message

    parsed = {"server": proxy["server"]}

    if proxy.get("bypass"):
        parsed["bypass"] = proxy["bypass"]

    if all(auhtorization):
        parsed["username"] = proxy["username"]
        parsed["password"] = proxy["password"]

    return parsed


def _search_proxy(proxy: Proxy) -> ProxySettings:
    """searches for a proxy server matching the specified broker criteria

    Args:
        proxy: The proxy configuration to search for.

    Returns:
        A 'playwright' compliant proxy configuration.
    """

    # remove max_shape from criteria
    criteria = proxy.get("criteria", {}).copy()
    criteria.pop("max_shape", None)

    server = search_proxy_servers(max_shape=1, **criteria)[0]

    return {"server": server}


def is_ipv4_address(address: str) -> bool:
    """If a proxy address conforms to a IPv4 address"""
    try:
        ipaddress.IPv4Address(address)
        return True
    except ipaddress.AddressValueError:
        return False


def parse_or_search_proxy(proxy: Proxy) -> ProxySettings:
    """
    Parses a proxy configuration or searches for a matching one via broker.
    """
    assert "server" in proxy, "Missing 'server' field in the proxy configuration."

    parsed_url = urlparse(proxy["server"])
    server_address = parsed_url.hostname

    if server_address is None:
        raise ValueError(f"Invalid proxy server format: {proxy['server']}")

    # Accept both IP addresses and domain names like 'gate.nodemaven.com'
    if is_ipv4_address(server_address) or re.match(
        r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", server_address
    ):
        return _parse_proxy(proxy)

    assert proxy["server"] == "broker", f"Unknown proxy server type: {proxy['server']}"

    return _search_proxy(proxy)
