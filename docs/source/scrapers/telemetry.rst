===============
Usage Analytics
===============

ScrapeGraphAI collects **anonymous** usage data by default to improve the library and guide development efforts.

**Events Captured**

We capture events in the following scenarios:

1. When a ``Graph`` finishes running.
2. When an exception is raised in one of the nodes.

**Data Collected**

The data captured is limited to:

- Operating System and Python version
- A persistent UUID to identify the session, stored in ``~/.scrapegraphai.conf``

Additionally, the following properties are collected:

.. code-block:: python

   properties = {
       "graph_name": graph_name,
       "llm_model": llm_model_name,
       "embedder_model": embedder_model_name,
       "source_type": source_type,
       "source": source,
       "execution_time": execution_time,
       "prompt": prompt,
       "schema": schema,
       "error_node": error_node_name,
       "exception": exception,
       "response": response,
       "total_tokens": total_tokens,
   }

For more details, refer to the `telemetry.py <https://github.com/VinciGit00/Scrapegraph-ai/blob/main/scrapegraphai/telemetry/telemetry.py>`_ module.

**Opting Out**

If you prefer not to participate in telemetry, you can opt out using any of the following methods:

1. **Programmatically Disable Telemetry**:

   Add the following code at the beginning of your script:

   .. code-block:: python

      from scrapegraphai import telemetry
      telemetry.disable_telemetry()

2. **Configuration File**:

   Set the ``telemetry_enabled`` key to ``false`` in ``~/.scrapegraphai.conf`` under the ``[DEFAULT]`` section:

   .. code-block:: ini

      [DEFAULT]
      telemetry_enabled = False

3. **Environment Variable**:

   - **For a Shell Session**:

     .. code-block:: bash

        export SCRAPEGRAPHAI_TELEMETRY_ENABLED=false

   - **For a Single Command**:

     .. code-block:: bash

        SCRAPEGRAPHAI_TELEMETRY_ENABLED=false python my_script.py

By following any of these methods, you can easily opt out of telemetry and ensure your usage data is not collected.
