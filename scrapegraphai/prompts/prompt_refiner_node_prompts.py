"""
Prompts refiner prompts helper
"""

TEMPLATE_REFINER = """
**Task**: Analyze the user's request and the provided JSON schema to clearly map the desired data extraction.\n
Break down the user's request into key components, and then explicitly connect these components to the 
corresponding elements within the JSON schema.

**User's Request**:
{user_input}

**Desired JSON Output Schema**:
```json
{json_schema}
```

**Analysis Instructions**:
1. **Break Down User Request:** 
* Clearly identify the core entities or data types the user is asking for.\n
* Highlight any specific attributes or relationships mentioned in the request.\n

2. **Map to JSON Schema**:
* For each identified element in the user request, pinpoint its exact counterpart in the JSON schema.\n
* Explain how the schema structure accommodates the user's needs.
* If applicable, mention any schema elements that are not directly addressed in the user's request.\n

This analysis will be used to guide the HTML structure examination and ultimately inform the code generation process.\n
Please generate only the analysis and no other text.

**Response**:
"""
        
TEMPLATE_REFINER_WITH_CONTEXT = """
**Task**: Analyze the user's request, the provided JSON schema, and the additional context the user provided to clearly map the desired data extraction.\n
Break down the user's request into key components, and then explicitly connect these components to the corresponding elements within the JSON schema.\n

**User's Request**:
{user_input}

**Desired JSON Output Schema**:
```json
{json_schema}
```

**Additional Context**:
{additional_context}

**Analysis Instructions**:
1. **Break Down User Request:** 
* Clearly identify the core entities or data types the user is asking for.\n
* Highlight any specific attributes or relationships mentioned in the request.\n

2. **Map to JSON Schema**:
* For each identified element in the user request, pinpoint its exact counterpart in the JSON schema.\n
* Explain how the schema structure accommodates the user's needs.\n
* If applicable, mention any schema elements that are not directly addressed in the user's request.\n

This analysis will be used to guide the HTML structure examination and ultimately inform the code generation process.\n
Please generate only the analysis and no other text.

**Response**:
"""
