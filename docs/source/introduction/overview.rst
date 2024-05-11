Overview 
========

In a world where web pages are constantly changing and in a data-hungry world there is a need for a new generation of scrapers, and this is where ScrapegraphAI was born. 
An opensource library with the aim of starting a new era of scraping tools that are more flexible and require less maintenance by developers, with the use of LLMs.

.. image:: ../../assets/scrapegraphai_logo.png
   :align: center
   :width: 100px
   :alt: ScrapegraphAI

Why ScrapegraphAI?
==================

ScrapegraphAI in our vision represents a significant step forward in the field of web scraping, offering an open-source solution designed to meet the needs of a constantly evolving web landscape. Here's why ScrapegraphAI stands out:

Flexibility and Adaptability
^^^^^^^^^^^^^^^^^^^^^^^^^^^
Traditional web scraping tools often rely on fixed patterns or manual configuration to extract data from web pages. ScrapegraphAI, leveraging the power of LLMs, adapts to changes in website structures, reducing the need for constant developer intervention. 
This flexibility ensures that scrapers remain functional even when website layouts change.


Overview
========
With ScrapegraphAI you first construct a pipeline of steps you want to execute by combining nodes into a graph.
Executing the graph takes care of all the steps that are often part of scraping: fetching, parsing etc...
Finally the scraped and processed data gets fed to an LLM which generates a response.

.. image:: ../../assets/project_overview_diagram.png
   :align: center
   :alt: ScrapegraphAI Overview