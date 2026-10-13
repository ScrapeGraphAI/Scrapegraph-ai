from unittest.mock import patch
import pytest
from fp.errors import FreeProxyException

from scrapegraphai.utils.proxy_rotation import (
    Proxy,
    _parse_proxy,
    _search_proxy,
    is_ipv4_address,
    parse_or_search_proxy,
    search_proxy_servers,
)


def test_search_proxy_servers_success():
    servers = search_proxy_servers(
        anonymous=True,
        countryset={"US"},
        secure=False,
        timeout=10.0,
        max_shape=2,
        search_outside_if_empty=True,
    )

    assert isinstance(servers, list)
    assert all(isinstance(server, str) for server in servers)


def test_search_proxy_servers_exception():
    with pytest.raises(FreeProxyException):
        search_proxy_servers(
            anonymous=True,
            countryset={"XX"},
            secure=True,
            timeout=1.0,
            max_shape=2,
            search_outside_if_empty=False,
        )


def test_parse_proxy_success():
    proxy = {
        "server": "192.168.1.1:8080",
        "username": "user",
        "password": "pass",
        "bypass": "*.local",
    }

    parsed_proxy = _parse_proxy(proxy)
    assert parsed_proxy == proxy


def test_parse_proxy_exception():
    invalid_proxy = {"server": "192.168.1.1:8080", "username": "user"}

    with pytest.raises(AssertionError) as error_info:
        _parse_proxy(invalid_proxy)

    assert "username and password must be provided in pairs" in str(error_info.value)


@patch("scrapegraphai.utils.proxy_rotation.search_proxy_servers", return_value=["http://103.10.63.135:8080"])
def test_search_proxy_success(mock_search):
    proxy = Proxy(criteria={"anonymous": True, "countryset": {"US"}})
    found_proxy = _search_proxy(proxy)

    assert isinstance(found_proxy, dict)
    assert "server" in found_proxy


def test_is_ipv4_address():
    assert is_ipv4_address("192.168.1.1") is True
    assert is_ipv4_address("999.999.999.999") is False
    assert is_ipv4_address("no-address") is False


@patch("scrapegraphai.utils.proxy_rotation.search_proxy_servers", return_value=["http://103.10.63.135:8080"])
def test_parse_or_search_proxy_success(mock_search):
    proxy = {
        "server": "192.168.1.1:8080",
        "username": "username",
        "password": "password",
    }

    parsed_proxy = parse_or_search_proxy(proxy)
    assert parsed_proxy == proxy

    proxy_domain = {
        "server": "gate.nodemaven.com:8080",
        "username": "user",
        "password": "pwd",
    }
    parsed_domain = parse_or_search_proxy(proxy_domain)
    assert parsed_domain == proxy_domain

    proxy_broker = {
        "server": "broker",
        "criteria": {
            "anonymous": True,
            "countryset": {"US"},
            "secure": True,
            "timeout": 10.0,
        },
    }

    found_proxy = parse_or_search_proxy(proxy_broker)

    assert isinstance(found_proxy, dict)
    assert "server" in found_proxy


def test_parse_or_search_proxy_exception():
    proxy = {
        "username": "username",
        "password": "password",
    }

    with pytest.raises(AssertionError) as error_info:
        parse_or_search_proxy(proxy)

    assert "missing server in the proxy configuration" in str(error_info.value)


def test_parse_or_search_proxy_unknown_server():
    proxy = {
        "server": "unknown",
    }

    with pytest.raises(AssertionError) as error_info:
        parse_or_search_proxy(proxy)

    assert "unknown proxy server" in str(error_info.value)


def test_parse_or_search_proxy_moves_url_credentials_out_of_server():
    for server in (
        "http://user:p%40ss%2Fw@gate.example.com:8080",
        "user:p%40ss%2Fw@gate.example.com:8080",
    ):
        parsed = parse_or_search_proxy({"server": server})
        assert parsed["username"] == "user"
        assert parsed["password"] == "p@ss/w"
        assert "@" not in parsed["server"]
        assert parsed["server"].endswith("gate.example.com:8080")


def test_parse_or_search_proxy_explicit_credentials_win_over_url():
    parsed = parse_or_search_proxy(
        {
            "server": "http://old:secret@gate.example.com:8080",
            "username": "user",
            "password": "pass",
        }
    )
    assert parsed == {
        "server": "http://gate.example.com:8080",
        "username": "user",
        "password": "pass",
    }


def test_parse_or_search_proxy_accepts_local_and_bare_hosts_with_a_port():
    for server in (
        "localhost:8888",
        "http://proxy:8080",
        "http://[::1]:8080",
        "socks5://gate.example.com:1080",
    ):
        assert parse_or_search_proxy({"server": server}) == {"server": server}


def test_parse_or_search_proxy_errors_do_not_show_the_password():
    with pytest.raises(AssertionError) as error_info:
        parse_or_search_proxy({"server": "http://user:secret@unknown"})

    assert "secret" not in str(error_info.value)
