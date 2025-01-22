Installation
------------

In the following sections I will guide you through the installation process of the required components
for this project.

Prerequisites
^^^^^^^^^^^^^

- `Python >=3.9 <https://www.python.org/downloads/>`_
- `pip <https://pip.pypa.io/en/stable/getting-started/>`_
- `Ollama <https://ollama.com/>`_ (optional for local models)


Install the library
^^^^^^^^^^^^^^^^^^^^

The library is available on PyPI, so it can be installed using the following command:

.. code-block:: bash

   pip install scrapegraphai

.. important::

   It is higly recommended to install the library in a virtual environment (conda, venv, etc.)

If your clone the repository, it is recommended to use a package manager like `uv <https://github.com/astral-sh/uv>`_.
To install the library using uv, you can run the following command:

.. code-block:: bash

   uv pin 3.10
   uv sync
   uv build

.. caution::

      **Rye** must be installed first by following the instructions on the `official website <https://github.com/astral-sh/uv>`_.

Additionally on Windows when using WSL
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you are using Windows Subsystem for Linux (WSL) and you are facing issues with the installation of the library, you might need to install the following packages:

.. code-block:: bash

   sudo apt-get -y install libnss3 libnspr4 libgbm1 libasound2
