"""
HTML analysis prompts helper
"""

TEMPLATE_HTML_ANALYSIS = """
Task: Your job is to analyze the provided HTML code in relation to the initial scraping task analysis and provide all the necessary HTML information useful for implementing a function that extracts data from the given HTML string.

**Initial Analysis**:
{initial_analysis}

**HTML Code**:
```html
{html_code}
```

**HTML Analysis Instructions**:
1. Examine the HTML code and identify elements, classes, or IDs that correspond to each required data field mentioned in the Initial Analysis.
2. Look for patterns or repeated structures that could indicate multiple items (e.g., product listings).
3. Note any nested structures or relationships between elements that are relevant to the data extraction task.
4. Discuss any additional considerations based on the specific HTML layout that are crucial for accurate data extraction.
5. Recommend the specific strategy to use for scraping the content, remeber.

**Important Notes**:
- The function that the code generator is gonig to implement will receive the HTML as a string parameter, not as a live webpage.
- No web scraping, automation, or handling of dynamic content is required.
- The analysis should focus solely on extracting data from the static HTML provided.
- Be precise and specific in your analysis, as the code generator will, possibly, not have access to the full HTML context.

This HTML analysis will be used to guide the final code generation process for a function that extracts data from the given HTML string.
Please provide only the analysis with relevant, specific information based on this HTML code. Avoid vague statements and focus on exact details needed for accurate data extraction.

Focus on providing a concise, step-by-step analysis of the HTML structure and the key elements needed for data extraction. Do not include any code examples or implementation logic. Keep the response focused and avoid general statements.**

**HTML Analysis for Data Extraction**:
"""

TEMPLATE_HTML_ANALYSIS_WITH_CONTEXT = """
Task: Your job is to analyze the provided HTML code in relation to the initial scraping task analysis and the additional context the user provided and provide all the necessary HTML information useful for implementing a function that extracts data from the given HTML string.

**Initial Analysis**:
{initial_analysis}

**HTML Code**:
```html
{html_code}
```

**Additional Context**:
{additional_context}

**HTML Analysis Instructions**:
1. Examine the HTML code and identify elements, classes, or IDs that correspond to each required data field mentioned in the Initial Analysis.
2. Look for patterns or repeated structures that could indicate multiple items (e.g., product listings).
3. Note any nested structures or relationships between elements that are relevant to the data extraction task.
4. Discuss any additional considerations based on the specific HTML layout that are crucial for accurate data extraction.
5. Recommend the specific strategy to use for scraping the content, remeber.

**Important Notes**:
- The function that the code generator is gonig to implement will receive the HTML as a string parameter, not as a live webpage.
- No web scraping, automation, or handling of dynamic content is required.
- The analysis should focus solely on extracting data from the static HTML provided.
- Be precise and specific in your analysis, as the code generator will, possibly, not have access to the full HTML context.

This HTML analysis will be used to guide the final code generation process for a function that extracts data from the given HTML string.
Please provide only the analysis with relevant, specific information based on this HTML code. Avoid vague statements and focus on exact details needed for accurate data extraction.

Focus on providing a concise, step-by-step analysis of the HTML structure and the key elements needed for data extraction. Do not include any code examples or implementation logic. Keep the response focused and avoid general statements.**
In your code do not include backticks.
**HTML Analysis for Data Extraction**:
"""
