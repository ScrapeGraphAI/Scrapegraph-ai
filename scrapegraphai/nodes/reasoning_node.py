"""
PromptRefinerNode Module
"""
from typing import List, Optional
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel
from langchain_core.utils.pydantic import is_basemodel_subclass
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langchain_mistralai import ChatMistralAI
from langchain_community.chat_models import ChatOllama
from tqdm import tqdm
from .base_node import BaseNode
from ..utils import transform_schema

class ReasoningNode(BaseNode):
    """
    A node that refine the user prompt with the use of the schema and additional context and
    create a precise prompt in subsequent steps that explicitly link elements in the user's 
    original input to their corresponding representations in the JSON schema.

    Attributes:
        llm_model: An instance of a language model client, configured for generating answers.
        verbose (bool): A flag indicating whether to show print statements during execution.

    Args:
        input (str): Boolean expression defining the input keys needed from the state.
        output (List[str]): List of output keys to be updated in the state.
        node_config (dict): Additional configuration for the node.
        node_name (str): The unique identifier name for the node, defaulting to "GenerateAnswer".
    """

    def __init__(
        self,
        input: str,
        output: List[str],
        node_config: Optional[dict] = None,
        node_name: str = "PromptRefiner",
    ):
        super().__init__(node_name, "node", input, output, 2, node_config)

        self.llm_model = node_config["llm_model"]

        if isinstance(node_config["llm_model"], ChatOllama):
            self.llm_model.format="json"

        self.verbose = (
            True if node_config is None else node_config.get("verbose", False)
        )
        self.force = (
            False if node_config is None else node_config.get("force", False)
        )
        self.script_creator = (
            False if node_config is None else node_config.get("script_creator", False)
        )
        self.is_md_scraper = (
            False if node_config is None else node_config.get("is_md_scraper", False)
        )

        self.additional_info = node_config.get("additional_info")
        
        self.output_schema = node_config.get("schema")

    def execute(self, state: dict) -> dict:
        """
        Generate a refined prompt using the user's prompt, the schema, and additional context.

        Args:
            state (dict): The current state of the graph. The input keys will be used
                            to fetch the correct data from the state.

        Returns:
            dict: The updated state with the output key containing the generated answer.

        Raises:
            KeyError: If the input keys are not found in the state, indicating
                      that the necessary information for generating an answer is missing.
        """

        self.logger.info(f"--- Executing {self.node_name} Node ---")

        user_prompt = state['user_prompt']

        self.simplefied_schema = transform_schema(self.output_schema.schema())
        
        if self.additional_info is not None:
            prompt = PromptTemplate(
                template=TEMPLATE_REFINER_WITH_CONTEXT,
                partial_variables={"user_input": user_prompt,
                                    "json_schema": str(self.simplefied_schema),
                                    "additional_context": self.additional_info})
        else:
            prompt = PromptTemplate(
                template=TEMPLATE_REFINER,
                partial_variables={"user_input": user_prompt,
                                    "json_schema": str(self.simplefied_schema)})

        output_parser = StrOutputParser()

        chain =  prompt | self.llm_model | output_parser
        refined_prompt = chain.invoke({})

        state.update({self.output[0]: refined_prompt})
        return state


TEMPLATE_REASONING = """
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
        
TEMPLATE_REASONING_WITH_CONTEXT = """
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

# TEMPLATE_REASONING_v1 (Emphasis on Clarity)
TEMPLATE_REASONING_v1 = """
**Task:** Meticulously analyze the user's request and the provided JSON schema to create a crystal-clear mapping for data extraction.

**User's Request:**
{user_input}

**Desired JSON Output Schema:**
```json
{json_schema}
```

**Analysis Steps:**

1. **Deconstruct User Request:** 
   * Pinpoint the core data the user needs (e.g., specific entities, attributes, relationships).
   * Highlight any filtering or sorting criteria mentioned in the request.

2. **Connect to JSON Schema:**
   * For each element the user wants, locate its precise match in the schema.
   * Explain how the schema's structure fulfills the user's needs (e.g., nested objects, arrays).
   * If any schema parts aren't relevant to the request, point them out.

**Remember:** 
* This analysis is crucial for building the HTML structure and generating code.
* Be thorough and explicit in your explanations.
* Focus solely on the analysis; avoid extraneous text.

**Response:**
"""

# TEMPLATE_REASONING_v2 (Focus on Data Transformation)
TEMPLATE_REASONING_v2 = """
**Task:** Analyze the user's request and the JSON schema to determine the necessary data transformations for extraction.

**User's Request:**
{user_input}

**Desired JSON Output Schema:**
```json
{json_schema}
```

**Analysis Steps:**

1. **Understand User's Needs:** 
   * Identify the specific data the user wants and how they want it presented.
   * Note any calculations, formatting, or restructuring required.

2. **Schema Mapping and Transformations:**
   * Match user's needs to schema elements, noting any data type conversions needed.
   * Outline the steps to transform the schema data into the user's desired format.
   * If the schema lacks necessary data, clearly state this.

**Key Points:** 
* This analysis guides how we'll manipulate the schema data to match the user's request.
* Be explicit about the transformations needed (e.g., filtering, renaming, calculations).
* Focus on the analysis; no additional text is required.

**Response:**
"""

# TEMPLATE_REASONING_v3 (Highlighting Potential Challenges)
TEMPLATE_REASONING_v3 = """
**Task:** Analyze the user's request and JSON schema, identifying potential challenges in data extraction.

**User's Request:**
{user_input}

**Desired JSON Output Schema:**
```json
{json_schema}
```

**Analysis Steps:**

1. **Thorough Request Understanding:** 
   * Clearly identify all data elements the user wants.
   * Note any ambiguities or complexities in the request.

2. **Schema Mapping and Challenges:**
   * Match user needs to schema elements, flagging any mismatches or missing data.
   * Highlight any complex schema structures that might complicate extraction.
   * If the request is vague, suggest clarifications needed from the user.

**Important Notes:** 
* This analysis helps us anticipate and address potential roadblocks in code generation.
* Be proactive in identifying challenges, not just mapping data.
* If the request is unclear, ask specific questions for clarification.
* Focus on the analysis; avoid any unnecessary text.

**Response:**
"""

# TEMPLATE_REASONING_v4 (Concise and Actionable)
TEMPLATE_REASONING_v4 = """
**Task:** Map user request to JSON schema, providing actionable insights for data extraction.

**User's Request:**
{user_input}

**Desired JSON Output Schema:**
```json
{json_schema}
```

**Analysis:**

* **Key Data:** [List the specific data elements the user wants]
* **Schema Mapping:** [Concisely map each desired element to its schema counterpart]
* **Transformations:** [Briefly list any data manipulations needed]
* **Challenges:** [Highlight any potential issues or ambiguities]

**Response:**
"""

# TEMPLATE_REASONING_v5 (Schema-Centric Approach)
TEMPLATE_REASONING_v5 = """
**Task:** Analyze the JSON schema to determine how it can fulfill the user's data request.

**User's Request:**
{user_input}

**Desired JSON Output Schema:**
```json
{json_schema}
```

**Analysis:**

1. **Schema Structure Breakdown:**
   * Describe the key entities, relationships, and nesting in the schema.
   * Highlight any relevant data types or formatting within the schema.

2. **Fulfilling User's Needs:**
   * Explain how the schema's structure can provide the data the user wants.
   * Point out any schema elements that directly address the user's request.
   * Identify any potential gaps or challenges in fulfilling the request.

**Remember:** 
* This analysis prioritizes understanding the schema's capabilities.
* Focus on how the schema's structure can be leveraged for data extraction.
* If the schema is insufficient, clearly state this and suggest potential solutions.
* Provide only the analysis; avoid any additional text.

**Response:**
"""

# TEMPLATE_REASONING_WITH_CONTEXT_v1 (Clarity with Context Integration)
TEMPLATE_REASONING_WITH_CONTEXT_v1 = """
**Task:** Carefully analyze the user's request, the provided JSON schema, and the additional context to create a precise mapping for data extraction.

**User's Request:**
{user_input}

**Desired JSON Output Schema:**
```json
{json_schema}
```

**Additional Context:**
{additional_context}

**Analysis Steps:**

1. **Integrate Context into Request Understanding:**
   * Combine the user's explicit request with the additional context to gain a deeper understanding of their needs.
   * Identify any implicit requirements or preferences hinted at in the context

2. **Deconstruct Enhanced Request:**
   * Pinpoint the core data the user needs (e.g., specific entities, attributes, relationships).
   * Highlight any filtering or sorting criteria mentioned in the request or implied by the context

3. **Connect to JSON Schema:**
   * For each element the user wants, locate its precise match in the schema
   * Explain how the schema's structure fulfills the user's needs (e.g., nested objects, arrays)
   * If any schema parts aren't relevant to the request, point them out.

**Remember:** 
* The additional context is crucial for refining the analysis and ensuring accurate data extraction
* Be thorough and explicit in your explanations.
* Focus solely on the analysis; avoid extraneous text.

**Response:**
"""

# TEMPLATE_REASONING_WITH_CONTEXT_v2 (Context-Driven Data Transformation)
TEMPLATE_REASONING_WITH_CONTEXT_v2 = """
**Task:** Analyze the user's request, JSON schema, and context to determine the data transformations needed for extraction.

**User's Request:**
{user_input}

**Desired JSON Output Schema:**
```json
{json_schema}
```

**Additional Context:**
{additional_context}

**Analysis Steps:**

1. **Contextual Understanding of User's Needs:**
   * Combine the request and context to fully grasp the desired data and its presentation
   * Note any calculations, formatting, or restructuring implied by the context.

2. **Schema Mapping and Contextual Transformations:**
   * Match user's needs to schema elements, considering context for data type conversions
   * Outline the steps to transform schema data into the user's desired format, as informed by the context
   * If the schema lacks necessary data, clearly state this

**Key Points:** 
* The context is vital for tailoring data transformations to the user's specific situation.
* Be explicit about the transformations needed, referencing the context where relevant
* Focus on the analysis; no additional text is required

**Response:**
"""

# TEMPLATE_REASONING_WITH_CONTEXT_v3 (Contextual Challenge Identification)
TEMPLATE_REASONING_WITH_CONTEXT_v3 = """
**Task:** Analyze the user's request, JSON schema, and context, identifying potential challenges in data extraction

**User's Request:**
{user_input}

**Desired JSON Output Schema:**
```json
{json_schema}
```

**Additional Context:**
{additional_context}

**Analysis Steps:**

1. **Context-Enhanced Request Understanding:**
   * Use the context to clarify any ambiguities or complexities in the request
   * Identify any implicit requirements or potential conflicts highlighted by the context

2. **Schema Mapping and Contextual Challenges:**
   * Match user needs to schema elements, flagging any mismatches or missing data, considering the context
   * Highlight any complex schema structures or contextual factors that might complicate extraction
   * If the request remains unclear even with context, suggest specific clarifications needed from the user

**Important Notes:** 
* The context is key for anticipating and addressing potential roadblocks in code generation
* Be proactive in identifying challenges, especially those arising from the context
* If further clarification is needed, ask
specific questions tailored to the context

* Focus on the analysis; avoid any unnecessary text

**Response:**
"""

# TEMPLATE_REASONING_WITH_CONTEXT_v4 (Concise and Actionable, with Context)
TEMPLATE_REASONING_WITH_CONTEXT_v4 = """
**Task:** Map user request to JSON schema, incorporating context for actionable insights.

**User's Request:**
{user_input}

**Desired JSON Output Schema:**
```json
{json_schema}
```

**Additional Context:**
{additional_context}

**Analysis:**

* **Key Data (Contextualized):** [List the specific data elements the user wants, considering the context]
* **Schema Mapping (Context-Aware):** [Concisely map each desired element to its schema counterpart, noting any context-driven adjustments]
* **Transformations (Context-Informed):** [Briefly list any data manipulations needed, taking the context into account]
* **Challenges (Contextual):** [Highlight any potential issues or ambiguities arising from the request or context]

**Response:**
"""

# TEMPLATE_REASONING_WITH_CONTEXT_v5 (Schema-Centric with Contextual Lens)
TEMPLATE_REASONING_WITH_CONTEXT_v5 = """
**Task:** Analyze the JSON schema through the lens of the user's request and context, determining how it can fulfill their needs

**User's Request:**
{user_input}

**Desired JSON Output Schema:**
```json
{json_schema}
```

**Additional Context:**
{additional_context}

**Analysis:**

1. **Schema Structure Breakdown (Contextualized):**
   * Describe the key entities, relationships, and nesting in the schema, highlighting those most relevant to the context
   * Point out any relevant data types or formatting within the schema that align with the context

2. **Fulfilling User's Needs (Context-Driven):**
   * Explain how the schema's structure, combined with the context, can provide the data the user wants
   * Identify any schema elements that directly or indirectly address the user's request, considering the context
   * Address any potential gaps or challenges in fulfilling the request, taking the context into account

**Remember:** 
* This analysis prioritizes understanding the schema's capabilities in relation to the specific context
* Focus on how the schema's structure, combined with the context, can be leveraged for data extraction
* If the schema is insufficient even with context, clearly state this and suggest potential solutions
* Provide only the analysis; avoid any additional text

**Response:**
"""
