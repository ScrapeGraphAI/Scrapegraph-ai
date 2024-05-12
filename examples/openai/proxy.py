from scrapegraphai.utils import search_proxy_servers

proxies = search_proxy_servers(
    anonymous=True,
    countryset={"IT"},
    # secure=True,
    timeout=1.0,
    max_shape=2
)

print(proxies)