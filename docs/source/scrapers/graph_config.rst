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
- `burr_kwargs`: A dictionary with additional parameters to enable `Burr` graphical user interface.
- `max_images`: The maximum number of images to be analyzed. Useful in `OmniScraperGraph` and `OmniSearchGraph`.
- `cache_path`: The path where the cache files will be saved. If already exists, the cache will be loaded from this path.
- `additional_info`: Add additional text to default prompts defined in the graphs.
.. _Burr:

Burr Integration
^^^^^^^^^^^^^^^^

`Burr` is an open source python library that allows the creation and management of state machine applications. Discover more about it `here <https://github.com/DAGWorks-Inc/burr>`_.
It is possible to enable a local hosted webapp to visualize the scraping pipelines and the data flow.
First, we need to install the `burr` library as follows:

.. code-block:: bash

    pip install scrapegraphai[burr]

and then run the graphical user interface as follows:

.. code-block:: bash

    burr

To log your graph execution in the platform, you need to set the `burr_kwargs` parameter in the graph configuration as follows:

.. code-block:: python

    graph_config = {
        "llm":{...},
        "burr_kwargs": {
            "project_name": "test-scraper",
            "app_instance_id":"some_id",
        }
    }

.. _Proxy:

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
