.. _Configuration:

Additional Parameters
=====================

It is possible to customize the behavior of the graphs by setting some configuration options.
Some interesting ones are:

- `verbose`: If set to `True`, some debug information will be printed to the console.
- `headless`: If set to `False`, the web browser will be opened on the URL requested and close right after the HTML is fetched.
- `max_results`: The maximum number of results to be fetched from the search engine. Useful in `SearchGraph`.
- `output_path`: The path where the output files will be saved. Useful in `SpeechGraph`.
- `loader_kwargs`: A dictionary with additional parameters to be passed to the `Loader` class, such as `proxy`.
- `max_images`: The maximum number of images to be analyzed. Useful in `OmniScraperGraph` and `OmniSearchGraph`.

Proxy Rotation
^^^^^^^^^^^^^^

It is possible to rotate the proxy by setting the `proxy` option in the graph configuration.
We provide a free proxy service which is based on `free-proxy <https://pypi.org/project/free-proxy/>`_ library and can be used as follows:

.. code-block:: python

    graph_config = {
        "llm":{...},
        "loader_kwargs": {
            "proxy" : {
                "server": "broker",
                "criteria": {
                    "anonymous": True,
                    "secure": True,
                    "countryset": {"IT"},
                    "timeout": 10.0,
                    "max_shape": 3
                },
            },
        },
    }

Do you have a proxy server? You can use it as follows:

.. code-block:: python

    graph_config = {
        "llm":{...},
        "loader_kwargs": {
            "proxy" : {
                "server": "http://your_proxy_server:port",
                "username": "your_username",
                "password": "your_password",
            },
        },
    }
