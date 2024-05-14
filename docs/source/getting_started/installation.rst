Installation
------------

In the following sections I will guide you through the installation process of the required components
for this project.

Prerequisites
^^^^^^^^^^^^^

- `Python >=3.9,<3.12 <https://www.python.org/downloads/>`_
- `pip <https://pip.pypa.io/en/stable/getting-started/>`_
- `Ollama <https://ollama.com/>`_ (optional for local models)


Install the library
^^^^^^^^^^^^^^^^^^^^

The library is available on PyPI, so it can be installed using the following command:

.. code-block:: bash

   pip install scrapegraphai

.. important::
   
   It is higly recommended to install the library in a virtual environment (conda, venv, etc.)

If your clone the repository, you can install the library using `poetry <https://python-poetry.org/docs/>`_:

.. code-block:: bash

   poetry install

Additionally on Windows when using WSL
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you are using Windows Subsystem for Linux (WSL) and you are facing issues with the installation of the library, you might need to install the following packages:

.. code-block:: bash

   sudo apt-get -y install libnss3 libnspr4 libgbm1 libasound2


