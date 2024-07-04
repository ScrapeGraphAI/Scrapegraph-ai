"""
Fireworks Module
"""
from langchain_fireworks import ChatFireworks


class Fireworks(ChatFireworks):
  """
  Initializes the Fireworks class.

  Args:
      llm_config (dict): A dictionary containing configuration parameters for the LLM (required).
          The specific keys and values will depend on the LLM implementation
          used by the underlying `ChatFireworks` class. Consult its documentation
          for details.

  Raises:
      ValueError: If required keys are missing from the llm_config dictionary.
  """

  def __init__(self, llm_config: dict):
      """
      Initializes the Fireworks class.

      Args:
          llm_config (dict): A dictionary containing configuration parameters for the LLM.
              The specific keys and values will depend on the LLM implementation.

      Raises:
          ValueError: If required keys are missing from the llm_config dictionary.
      """

      super().__init__(**llm_config)
