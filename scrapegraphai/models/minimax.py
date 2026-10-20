"""
MiniMax Module
"""

from langchain_openai import ChatOpenAI

DEFAULT_MINIMAX_OPENAI_BASE_URL = "https://api.minimax.io/v1"


class MiniMax(ChatOpenAI):
    """
    A wrapper for the ChatOpenAI class (MiniMax uses an OpenAI-compatible API) that
    provides default configuration and could be extended with additional methods
    if needed.

    Args:
        llm_config (dict): Configuration parameters for the language model.
    """

    def __init__(self, **llm_config):
        if "model" not in llm_config and "model_name" not in llm_config:
            llm_config["model"] = "MiniMax-M3.1-Flash"
        if "api_key" in llm_config:
            llm_config["openai_api_key"] = llm_config.pop("api_key")
        if "base_url" not in llm_config and "openai_api_base" not in llm_config:
            llm_config["openai_api_base"] = DEFAULT_MINIMAX_OPENAI_BASE_URL

        super().__init__(**llm_config)

    def _get_request_payload(self, input_, *, stop=None, **kwargs):
        payload = super()._get_request_payload(input_, stop=stop, **kwargs)
        # ChatOpenAI only serializes standard message fields. MiniMax requires
        # its separate reasoning field to be replayed alongside tool calls.
        if "messages" in payload:
            messages = self._convert_input(input_).to_messages()
            for message, serialized in zip(messages, payload["messages"]):
                if serialized["role"] == "assistant":
                    reasoning = message.additional_kwargs.get("reasoning_content")
                    if reasoning is not None:
                        serialized["reasoning_content"] = reasoning
        return payload

    def _create_chat_result(self, response, generation_info=None):
        result = super()._create_chat_result(response, generation_info)
        response_dict = (
            response if isinstance(response, dict) else response.model_dump()
        )
        for generation, choice in zip(result.generations, response_dict["choices"]):
            reasoning = choice["message"].get("reasoning_content")
            if reasoning is not None:
                generation.message.additional_kwargs["reasoning_content"] = reasoning
        return result

    def _convert_chunk_to_generation_chunk(
        self, chunk, default_chunk_class, base_generation_info
    ):
        generation = super()._convert_chunk_to_generation_chunk(
            chunk, default_chunk_class, base_generation_info
        )
        choices = chunk.get("choices") or chunk.get("chunk", {}).get("choices", [])
        if generation is not None and choices:
            reasoning = (choices[0].get("delta") or {}).get("reasoning_content")
            if reasoning is not None:
                generation.message.additional_kwargs["reasoning_content"] = reasoning
        return generation
