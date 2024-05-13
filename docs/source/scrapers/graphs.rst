Graphs
======

Graphs are scraping pipelines aimed at solving specific tasks. They are composed by nodes which can be configured individually to address different aspects of the task (fetching data, extracting information, etc.).

There are currently three types of graphs available in the library:

- **SmartScraperGraph**: one-page scraper that requires a user-defined prompt and a URL (or local file) to extract information from using LLM.
- **SearchGraph**: multi-page scraper that only requires a user-defined prompt to extract information from a search engine using LLM. It is built on top of SmartScraperGraph.
- **SpeechGraph**: text-to-speech pipeline that generates an answer as well as a requested audio file. It is built on top of SmartScraperGraph and requires a user-defined prompt and a URL (or local file).

**Note:** they all use a graph configuration to set up LLM models and other parameters. To find out more about the configurations, check the `LLM`_ and `Configuration`_ sections.

SmartScraperGraph
^^^^^^^^^^^^^^^^^

.. image:: ../../assets/smartscrapergraph.png
   :align: center
   :width: 90%
   :alt: SmartScraperGraph
|

First we define the graph configuration, which includes the LLM model and other parameters. Then we create an instance of the SmartScraperGraph class, passing the prompt, source, and configuration as arguments. Finally, we run the graph and print the result.
It will fetch the data from the source and extract the information based on the prompt in JSON format.

.. code-block:: python

   from scrapegraphai.graphs import SmartScraperGraph

   graph_config = {
      "llm": {...},
   }

   smart_scraper_graph = SmartScraperGraph(
      prompt="List me all the projects with their descriptions",
      source="https://perinim.github.io/projects",
      config=graph_config
   )

   result = smart_scraper_graph.run()
   print(result)


SearchGraph
^^^^^^^^^^^

.. image:: ../../assets/searchgraph.png
   :align: center
   :width: 80%
   :alt: SearchGraph
|

Similar to SmartScraperGraph, we define the graph configuration, create an instance of the SearchGraph class, and run the graph.
It will create a search query, fetch the first n results from the search engine, run n SmartScraperGraph instances, and return the results in JSON format.


.. code-block:: python

   from scrapegraphai.graphs import SearchGraph

   graph_config = {
      "llm": {...},
      "embeddings": {...},
   }

   # Create the SearchGraph instance
   search_graph = SearchGraph(
      prompt="List me all the traditional recipes from Chioggia",
      config=graph_config
   )

   # Run the graph
   result = search_graph.run()
   print(result)


SpeechGraph
^^^^^^^^^^^

.. image:: ../../assets/speechgraph.png
   :align: center
   :width: 90%
   :alt: SpeechGraph
|

Similar to SmartScraperGraph, we define the graph configuration, create an instance of the SpeechGraph class, and run the graph.
It will fetch the data from the source, extract the information based on the prompt, and generate an audio file with the answer, as well as the answer itself, in JSON format.

.. code-block:: python

   from scrapegraphai.graphs import SpeechGraph

   graph_config = {
      "llm": {...},
      "tts_model": {...},
   }

   # ************************************************
   # Create the SpeechGraph instance and run it
   # ************************************************

   speech_graph = SpeechGraph(
      prompt="Make a detailed audio summary of the projects.",
      source="https://perinim.github.io/projects/",
      config=graph_config,
   )

   result = speech_graph.run()
   print(result)