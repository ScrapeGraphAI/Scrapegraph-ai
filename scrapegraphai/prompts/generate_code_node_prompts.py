"""
Generate code prompts helper
"""

TEMPLATE_INIT_CODE_GENERATION = """
**Task**: Create a Python function named `extract_data(html: str) -> dict()` using BeautifulSoup that extracts relevant information from the given HTML code string and returns it in a dictionary matching the Desired JSON Output Schema.

**User's Request**:
{user_input}

**Desired JSON Output Schema**:
```json
{json_schema}
```

**Initial Task Analysis**:
{initial_analysis}

**HTML Code**:
```html
{html_code}
```

**HTML Structure Analysis**:
{html_analysis}

Based on the above analyses, generate the `extract_data(html: str) -> dict()` function that:
1. Efficiently extracts the required data from the given HTML structure.
2. Processes and structures the data according to the specified JSON schema.
3. Returns the structured data as a dictionary.

Your code should be well-commented, explaining the reasoning behind key decisions and any potential areas for improvement or customization.

Use only the following pre-imported libraries:
- BeautifulSoup from bs4
- re

**Output ONLY the Python code of the extract_data function, WITHOUT ANY IMPORTS OR ADDITIONAL TEXT.**
In your code do not include backticks.

**Response**:
"""

TEMPLATE_SYNTAX_ANALYSIS = """
The current code has encountered a syntax error. Here are the details:

Current Code:
```python
{generated_code}
```

Syntax Error:
{errors}

Please analyze in detail the syntax error and suggest a fix. Focus only on correcting the syntax issue while ensuring the code still meets the original requirements.

Provide your analysis and suggestions for fixing the error. DO NOT generate any code in your response.
"""

TEMPLATE_SYNTAX_CODE_GENERATION = """
Based on the following analysis of a syntax error, please generate the corrected code, following the suggested fix.:

Error Analysis:
{analysis}

Original Code:
```python
{generated_code}
```

Generate the corrected code, applying the suggestions from the analysis. Output ONLY the corrected Python code, WITHOUT ANY ADDITIONAL TEXT.
"""

TEMPLATE_EXECUTION_ANALYSIS = """
The current code has encountered an execution error. Here are the details:

**Current Code**:
```python
{generated_code}
```

**Execution Error**:
{errors}

**HTML Code**:
```html
{html_code}
```

**HTML Structure Analysis**:
{html_analysis}

Please analyze the execution error and suggest a fix. Focus only on correcting the execution issue while ensuring the code still meets the original requirements and maintains correct syntax.
The suggested fix should address the execution error and ensure the function can successfully extract the required data from the provided HTML structure. Be sure to be precise and specific in your analysis.

Provide your analysis and suggestions for fixing the error. DO NOT generate any code in your response.
"""

TEMPLATE_EXECUTION_CODE_GENERATION = """
Based on the following analysis of an execution error, please generate the corrected code:

Error Analysis:
{analysis}

Original Code:
```python
{generated_code}
```

Generate the corrected code, applying the suggestions from the analysis. Output ONLY the corrected Python code, WITHOUT ANY ADDITIONAL TEXT.
"""

TEMPLATE_VALIDATION_ANALYSIS = """
The current code's output does not match the required schema. Here are the details:

Current Code:
```python
{generated_code}
```

Validation Errors:
{errors}

Required Schema:
```json
{json_schema}
```

Current Output:
{execution_result}

Please analyze the validation errors and suggest fixes. Focus only on correcting the output to match the required schema while ensuring the code maintains correct syntax and execution.

Provide your analysis and suggestions for fixing the error. DO NOT generate any code in your response.
"""

TEMPLATE_VALIDATION_CODE_GENERATION = """
Based on the following analysis of a validation error, please generate the corrected code:

Error Analysis:
{analysis}

Original Code:
```python
{generated_code}
```

Required Schema:
```json
{json_schema}
```

Generate the corrected code, applying the suggestions from the analysis and ensuring the output matches the required schema. Output ONLY the corrected Python code, WITHOUT ANY ADDITIONAL TEXT.
"""

TEMPLATE_SEMANTIC_COMPARISON = """
Compare the Generated Result with the Reference Result and determine if they are semantically equivalent:

Generated Result:
{generated_result}

Reference Result (Correct Output):
{reference_result}

Analyze the content, structure, and meaning of both results. They should be considered semantically equivalent if they convey the same information, even if the exact wording or structure differs.
If they are not semantically equivalent, identify what are the key differences in the Generated Result. The Reference Result should be considered the correct output, you need to pinpoint the problems in the Generated Result.

{format_instructions}

Human: Are the generated result and reference result semantically equivalent? If not, what are the key differences?

Assistant: Let's analyze the two results carefully:
"""

TEMPLATE_SEMANTIC_ANALYSIS = """
The current code's output is semantically different from the reference answer. Here are the details:

Current Code:
```python
{generated_code}
```

Semantic Differences:
{differences}

Comparison Explanation:
{explanation}

Please analyze these semantic differences and suggest how to modify the code to produce a result that is semantically equivalent to the reference answer. Focus on addressing the key differences while maintaining the overall structure and functionality of the code.

Provide your analysis and suggestions for fixing the semantic differences. DO NOT generate any code in your response.
"""

TEMPLATE_SEMANTIC_CODE_GENERATION = """
Based on the following analysis of semantic differences, please generate the corrected code:

Semantic Analysis:
{analysis}

Original Code:
```python
{generated_code}
```

Generated Result:
{generated_result}

Reference Result:
{reference_result}

Generate the corrected code, applying the suggestions from the analysis to make the output semantically equivalent to the reference result. Output ONLY the corrected Python code, WITHOUT ANY ADDITIONAL TEXT.
"""
