.. image:: ../../assets/scrapegraphai_logo.png
   :align: center
   :width: 50%
   :alt: ScrapegraphAI

Overview 
========

ScrapeGraphAI is a open-source web scraping python library designed to usher in a new era of scraping tools.
In today's rapidly evolving and data-intensive digital landscape, this library stands out by integrating LLM and
direct graph logic to automate the creation of scraping pipelines for websites and various local documents, including XML,
HTML, JSON, and more.

Simply specify the information you need to extract, and ScrapeGraphAI handles the rest,
providing a more flexible and low-maintenance solution compared to traditional scraping tools.

Why ScrapegraphAI?
==================

Traditional web scraping tools often rely on fixed patterns or manual configuration to extract data from web pages.
ScrapegraphAI, leveraging the power of LLMs, adapts to changes in website structures, reducing the need for constant developer intervention. 
This flexibility ensures that scrapers remain functional even when website layouts change.

We support many Large Language Models (LLMs) including GPT, Gemini, Groq, Azure, Hugging Face etc.
as well as local models which can run on your machine using Ollama.

Library Diagram
===============

With ScrapegraphAI you first construct a pipeline of steps you want to execute by combining nodes into a graph.
Executing the graph takes care of all the steps that are often part of scraping: fetching, parsing etc...
Finally the scraped and processed data gets fed to an LLM which generates a response.

.. image:: ../../assets/project_overview_diagram.png
   :align: center
   :width: 70%
   :alt: ScrapegraphAI Overview
