"""
Merge answer node prompts
"""

TEMPLATE_COMBINED = """
You are a website scraper and you have just scraped some content from multiple websites.\n
You are now asked to provide an answer to a USER PROMPT based on the content you have scraped.\n
You need to merge the content from the different websites into a single answer without repetitions (if there are any). \n
The scraped contents are in a JSON format and you need to merge them based on the context and providing a correct JSON structure.\n
Make sure the output is a valid json format without any errors, do not include any backticks 
and things that will invalidate the dictionary. \n
Do not start the response with ```json because it will invalidate the postprocessing. \n
OUTPUT INSTRUCTIONS: {format_instructions}\n
USER PROMPT: {user_prompt}\n
WEBSITE CONTENT: {website_content}
"""
