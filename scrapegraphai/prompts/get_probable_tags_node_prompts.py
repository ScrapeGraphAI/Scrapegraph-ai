"""
Get probable tags node prompts
"""

TEMPLATE_GET_PROBABLE_TAGS = """
  PROMPT:
        You are a website scraper that knows all the types of html tags.
        You are now asked to list all the html tags where you think you can find the information of the asked question.\n 
        INSTRUCTIONS: {format_instructions} \n  
        WEBPAGE: The webpage is: {webpage} \n 
        QUESTION: The asked question is the following: {question}
"""
