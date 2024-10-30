"""
This module contains prompts for description nodes in the ScrapeGraphAI application.
"""

DESCRIPTION_NODE_PROMPT = """
You are a  scraper and you have just scraped the
following content from a website. \n
Please provide a description summary of maximum of 20 words. \n
CONTENT OF THE WEBSITE: {content}
"""
