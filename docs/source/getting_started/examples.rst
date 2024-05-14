Examples
========

Let's suppose you want to scrape a website to get a list of projects with their descriptions.
You can use the `SmartScraperGraph` class to do that.
The following examples show how to use the `SmartScraperGraph` class with OpenAI models and local models.

OpenAI models
^^^^^^^^^^^^^

.. code-block:: python

   import os
   from dotenv import load_dotenv
   from scrapegraphai.graphs import SmartScraperGraph
   from scrapegraphai.utils import prettify_exec_info

   load_dotenv()

   openai_key = os.getenv("OPENAI_APIKEY")

   graph_config = {
      "llm": {
         "api_key": openai_key,
         "model": "gpt-3.5-turbo",
      },
   }

   # ************************************************
   # Create the SmartScraperGraph instance and run it
   # ************************************************

   smart_scraper_graph = SmartScraperGraph(
      prompt="List me all the projects with their description.",
      # also accepts a string with the already downloaded HTML code
      source="https://perinim.github.io/projects/",
      config=graph_config
   )

   result = smart_scraper_graph.run()
   print(result)


Local models
^^^^^^^^^^^^^

Remember to have installed in your pc ollama `ollama <https://ollama.com/>`
Remember to pull the right model for LLM and for the embeddings, like:

.. code-block:: bash

   ollama pull llama3
   ollama pull nomic-embed-text
   ollama pull mistral

After that, you can run the following code, using only your machine resources brum brum brum:

.. code-block:: python

   from scrapegraphai.graphs import SmartScraperGraph
   from scrapegraphai.utils import prettify_exec_info

   graph_config = {
      "llm": {
         "model": "ollama/mistral",
         "temperature": 1,
         "format": "json",  # Ollama needs the format to be specified explicitly
         "model_tokens": 2000, #  depending on the model set context length
         "base_url": "http://localhost:11434",  # set ollama URL of the local host (YOU CAN CHANGE IT, if you have a different endpoint
      },
      "embeddings": {
         "model": "ollama/nomic-embed-text",
         "temperature": 0,
         "base_url": "http://localhost:11434",  # set ollama URL
      }
   }

   # ************************************************
   # Create the SmartScraperGraph instance and run it
   # ************************************************

   smart_scraper_graph = SmartScraperGraph(
      prompt="List me all the projects with their description.",
      # also accepts a string with the already downloaded HTML code
      source="https://perinim.github.io/projects",
      config=graph_config
   )

   result = smart_scraper_graph.run()
   print(result)

To find out how you can customize the `graph_config` dictionary, by using different LLM and adding new parameters, check the `Scrapers` section!