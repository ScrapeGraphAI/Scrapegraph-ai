"""
Search internet node prompts helper
"""

TEMPLATE_SEARCH_INTERNET = """
PROMPT:
You are a search engine and you need to generate a search query based on the user's prompt. \n
Given the following user prompt, return a query that can be 
used to search the internet for relevant information. \n
You should return only the query string without any additional sentences. \n
For example, if the user prompt is "What is the capital of France?",
you should return "capital of France". \n
If you return something else, you will get a really bad grade. \n
What you return should be sufficient to get the answer from the internet. \n
Don't just return a small part of the prompt, unless that is sufficient. \n
USER PROMPT: {user_prompt}"""
