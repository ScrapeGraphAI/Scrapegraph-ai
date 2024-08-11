"""
Search internet node prompts helper
"""

template_search_internet = """
PROMPT:
You are a search engine and you need to generate a search query based on the user's prompt. \n
Given the following user prompt, return a query that can be 
used to search the internet for relevant information. \n
You should return only the query string without any additional sentences. \n
For example, if the user prompt is "What is the capital of France?",
you should return "capital of France". \n
If you return something else, you will get a really bad grade. \n
USER PROMPT: {user_prompt}"""