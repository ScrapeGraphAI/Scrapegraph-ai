scrapegraphai.helpers.models_tokens module
==========================================

.. automodule:: scrapegraphai.helpers.models_tokens
   :members:
   :undoc-members:
   :show-inheritance:

This module contains a comprehensive dictionary of AI models and their corresponding token limits. The `models_tokens` dictionary is organized by provider (e.g., OpenAI, Azure OpenAI, Google AI, etc.) and includes various models with their maximum token counts.

Example usage:

.. code-block:: python

   from scrapegraphai.helpers.models_tokens import models_tokens

   # Get the token limit for GPT-4
   gpt4_limit = models_tokens['openai']['gpt-4']
   print(f"GPT-4 token limit: {gpt4_limit}")

   # Check the token limit for a specific model
   model_name = "gpt-3.5-turbo"
   if model_name in models_tokens['openai']:
       print(f"{model_name} token limit: {models_tokens['openai'][model_name]}")
   else:
       print(f"{model_name} not found in the models list")

This information is crucial for users to understand the capabilities and limitations of different AI models when designing their scraping pipelines.