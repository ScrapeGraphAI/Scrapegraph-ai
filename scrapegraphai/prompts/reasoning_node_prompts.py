"""
Reasoning prompts helper module
"""

TEMPLATE_REASONING = """
**Task**: Analyze the user's request and the provided JSON schema to guide an LLM in extracting information directly from a markdown file previously parsed froma a HTML file.

**User's Request**:
{user_input}

**Target JSON Schema**:
```json
{json_schema}
```

**Analysis Instructions**:
1. **Interpret User Request:** 
* Identify the key information types or entities the user is seeking.
* Note any specific attributes, relationships, or constraints mentioned.

2. **Map to JSON Schema**:
* For each identified element in the user request, locate its corresponding field in the JSON schema.
* Explain how the schema structure represents the requested information.
* Highlight any relevant schema elements not explicitly mentioned in the user's request.

3. **Data Transformation Guidance**:
* Provide guidance on any necessary transformations to align extracted data with the JSON schema requirements.

This analysis will be used to instruct an LLM that has the HTML content in its context. The LLM will use this guidance to extract the information and return it directly in the specified JSON format.

**Reasoning Output**:
[Your detailed analysis based on the above instructions]
"""

TEMPLATE_REASONING_WITH_CONTEXT = """
**Task**: Analyze the user's request and the provided JSON schema to guide an LLM in extracting information directly from a markdown file previously parsed froma a HTML file.

**User's Request**:
{user_input}

**Target JSON Schema**:
```json
{json_schema}
```

**Additional Context**:
{additional_context}

**Analysis Instructions**:
1. **Interpret User Request and Context:** 
* Identify the key information types or entities the user is seeking.
* Note any specific attributes, relationships, or constraints mentioned.
* Incorporate insights from the additional context to refine understanding of the task.

2. **Map to JSON Schema**:
* For each identified element in the user request, locate its corresponding field in the JSON schema.
* Explain how the schema structure represents the requested information.
* Highlight any relevant schema elements not explicitly mentioned in the user's request.

3. **Extraction Strategy**:
* Based on the additional context, suggest specific strategies for locating and extracting the required information from the HTML.
* Highlight any potential challenges or special considerations mentioned in the context.

4. **Data Transformation Guidance**:
* Provide guidance on any necessary transformations to align extracted data with the JSON schema requirements.
* Note any special formatting, validation, or business logic considerations from the additional context.

This analysis will be used to instruct an LLM that has the HTML content in its context. The LLM will use this guidance to extract the information and return it directly in the specified JSON format.

**Reasoning Output**:
[Your detailed analysis based on the above instructions, incorporating insights from the additional context]
"""
