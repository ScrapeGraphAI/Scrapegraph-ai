Installation
------------

In the following sections I will guide you through the installation process of the required components
for this project.

Prerequisites
^^^^^^^^^^^^^

- `Python 3.8+ <https://www.python.org/downloads/>`_
- `Visual Studio Code <https://code.visualstudio.com/download>`_ or IDE of your choice

External dependencies
^^^^^^^^^^^^^^^^^^^^^

Windows
+++++++

Insert external dependencies for Windows if there are any.

Linux
++++++

You don't need to install any external dependencies.

Clone the repository
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   git clone https://github.com/VinciGit00/yoso-ai.git
   cd AmazScraper

Create a virtual environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It is recommended to create a virtual environment to install the dependencies in order to avoid conflicts with other projects.

.. code-block:: bash

   python -m venv venv
   # python3 -m venv venv

Activate the virtual environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All the commands must be executed in the virtual environment. If you are not familiar with virtual environments, please read the `Python Virtual Environments: A Primer <https://realpython.com/python-virtual-environments-a-primer/>`_ article.

To activate the virtual environment, run the following command:

.. code-block:: bash

   # Windows
   .\venv\Scripts\activate
   # Linux
   source venv/bin/activate

Install the dependencies
^^^^^^^^^^^^^^^^^^^^^^^^

In the **requirements.txt** file you will find all the dependencies needed to run the code. To install them, run the following command:

.. code-block:: bash

   pip install -r requirements.txt
   # pip3 install -r requirements.txt

Test the installation
^^^^^^^^^^^^^^^^^^^^^

- Let's test if the installation was successful. Run the following command:

    .. code-block:: bash

       python some_example.py
       # python3 .some_example.py

- Let's test if the modules works. Run the following command:

    .. code-block:: bash

       python -m examples.values_scraping
       # or
       python -m examples.html_scraping