"""
Search link node prompts helper
"""

TEMPLATE_RELEVANT_LINKS = """
You are a website scraper and you have just scraped the following content from a website.
Content: {content}

Assume relevance broadly, including any links that might be related or potentially useful 
in relation to the task.

Sort it in order of importance, the first one should be the most important one, the last one
the least important

Please list only valid URLs and make sure to err on the side of inclusion if it's uncertain 
whether the content at the link is directly relevant.

Output only a list of relevant links in the format:
[
    "link1",
    "link2",
    "link3",
    .
    .
    .
]
"""
