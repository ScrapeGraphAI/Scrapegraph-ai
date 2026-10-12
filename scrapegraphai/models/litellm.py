"""
LiteLLM Module
"""

import math
from typing import Any, Dict, List, Optional, Tuple

from langchain_core.callbacks import (
    AsyncCallbackManagerForLLMRun,
    CallbackManagerForLLMRun,
)
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, convert_to_openai_messages
from langchain_core.messages.ai import UsageMetadata
from langchain_core.outputs import ChatGeneration, ChatResult
from pydantic import ConfigDict, Field, model_validator

LITELLM_INSTALL_HINT = (
    "The litellm package is not installed. "
    "Please install it using `pip install scrapegraphai[litellm]`."
)


def _import_litellm():
    try:
        import litellm
    except ImportError as exc:
        raise ImportError(LITELLM_INSTALL_HINT) from exc
    return litellm


def get_litellm_model_tokens(model: str) -> Optional[int]:
    """
    Look up the max input tokens of a model in LiteLLM's model map.

    Args:
        model (str): A LiteLLM model name, e.g. ``anthropic/claude-sonnet-4-6``.

    Returns:
        Optional[int]: The context window, or None if LiteLLM does not know it.
    """
    litellm = _import_litellm()
    try:
        info = litellm.get_model_info(model)
    except Exception as exc:
        if not _is_model_not_mapped(exc):
            raise
        return None
    # ``max_tokens`` in LiteLLM's model map is usually the output limit, so it
    # is not used as a context window; unknown windows fall back to the
    # graph's default instead.
    return info.get("max_input_tokens") or None


def get_litellm_token_costs(
    model: str, prompt_tokens: int, completion_tokens: int, usage: Any = None
) -> Optional[Tuple[float, float]]:
    """
    Split the cost of a call into prompt and completion cost with LiteLLM's
    price map.

    Args:
        model (str): A LiteLLM model name, e.g. ``anthropic/claude-sonnet-4-6``.
        prompt_tokens (int): Number of prompt tokens.
        completion_tokens (int): Number of completion tokens.
        usage: The response usage object, so cached tokens are priced too.

    Returns:
        Optional[Tuple[float, float]]: ``(prompt_cost, completion_cost)`` in
        USD, or None if LiteLLM cannot price the model.
    """
    litellm = _import_litellm()
    try:
        prompt_cost, completion_cost = litellm.cost_per_token(
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            usage_object=usage,
        )
    except Exception:
        # The split only refines a cost LiteLLM already reported, so a failure
        # here must not fail a completion that succeeded.
        return None
    return float(prompt_cost), float(completion_cost)


def _is_model_not_mapped(exc: Exception) -> bool:
    """
    Whether ``exc`` is how LiteLLM reports a model missing from its model map.

    litellm 1.94 raises a bare ``Exception``; newer releases raise
    ``ModelNotMappedError``, and ``BadRequestError`` when no provider can be
    inferred from the model name (e.g. a proxy alias).
    """
    if type(exc) is Exception:
        return True
    try:
        from litellm.exceptions import BadRequestError
    except ImportError:
        BadRequestError = None
    try:
        from litellm.exceptions import ModelNotMappedError
    except ImportError:
        ModelNotMappedError = None
    known = tuple(e for e in (BadRequestError, ModelNotMappedError) if e is not None)
    return bool(known) and isinstance(exc, known)


class LiteLLM(BaseChatModel):
    """
    A chat model that calls the LiteLLM SDK, so any provider LiteLLM supports
    (OpenAI, Anthropic, Gemini, Bedrock, Vertex AI, Azure, Groq, Ollama, ...)
    can be used with a ``litellm/<provider>/<model>`` model string.

    Credentials are read by LiteLLM from the provider's usual environment
    variables (``ANTHROPIC_API_KEY``, ``AWS_*``, ...) unless ``api_key`` is set.
    ``drop_params`` defaults to True so OpenAI-only parameters are dropped for
    providers that do not accept them.

    Args:
        llm_config (dict): Configuration parameters for the language model.
    """

    model_config = ConfigDict(populate_by_name=True, protected_namespaces=())

    model: str
    api_key: Optional[str] = None
    api_base: Optional[str] = Field(default=None, alias="base_url")
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    timeout: Optional[float] = None
    max_retries: Optional[int] = None
    drop_params: bool = True
    # Set by AbstractGraph for every provider; responses are returned whole.
    streaming: bool = False
    model_kwargs: Dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def _collect_model_kwargs(cls, values: Any) -> Any:
        """Forward unknown config keys (top_p, seed, ...) to LiteLLM."""
        if not isinstance(values, dict):
            return values
        known = set(cls.model_fields) | {"base_url"}
        extra = {k: v for k, v in values.items() if k not in known}
        if not extra:
            return values
        values = {k: v for k, v in values.items() if k in known}
        values["model_kwargs"] = {**values.get("model_kwargs", {}), **extra}
        return values

    @property
    def _llm_type(self) -> str:
        return "litellm"

    @property
    def model_name(self) -> str:
        """Model name used by the graph for logging and cost tracking."""
        return self.model

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {"model": self.model, "api_base": self.api_base}

    def _completion_params(
        self, messages: List[BaseMessage], stop: Optional[List[str]], **kwargs: Any
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "model": self.model,
            "messages": convert_to_openai_messages(messages),
            "drop_params": self.drop_params,
        }
        optional = {
            "api_key": self.api_key,
            "api_base": self.api_base,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "timeout": self.timeout,
            "num_retries": self.max_retries,
            "stop": stop,
        }
        # Unset values are left out so LiteLLM falls back to provider env vars
        # and provider defaults.
        params.update({k: v for k, v in optional.items() if v is not None})
        params.update(self.model_kwargs)
        params.update(kwargs)
        return params

    def _create_chat_result(self, response: Any) -> ChatResult:
        choice = response.choices[0]
        usage = getattr(response, "usage", None)
        hidden_params = getattr(response, "_hidden_params", None) or {}

        usage_metadata = None
        token_usage: Dict[str, int] = {}
        input_tokens = output_tokens = 0
        if usage is not None:
            input_tokens = getattr(usage, "prompt_tokens", 0) or 0
            output_tokens = getattr(usage, "completion_tokens", 0) or 0
            total_tokens = getattr(usage, "total_tokens", 0) or (
                input_tokens + output_tokens
            )
            usage_metadata = UsageMetadata(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
            )
            token_usage = {
                "prompt_tokens": input_tokens,
                "completion_tokens": output_tokens,
                "total_tokens": total_tokens,
            }

        response_metadata: Dict[str, Any] = {
            "model_name": getattr(response, "model", None) or self.model,
            "finish_reason": getattr(choice, "finish_reason", None),
        }
        if hidden_params.get("response_cost") is not None:
            response_metadata["response_cost"] = hidden_params["response_cost"]
            costs = get_litellm_token_costs(
                self.model, input_tokens, output_tokens, usage=usage
            )
            # Only report the split when it adds up to what LiteLLM charged,
            # e.g. not for a proxy alias priced under the upstream model name.
            if costs is not None and math.isclose(
                sum(costs), float(hidden_params["response_cost"]), rel_tol=1e-6
            ):
                response_metadata["prompt_cost"] = costs[0]
                response_metadata["completion_cost"] = costs[1]

        message = AIMessage(
            content=choice.message.content or "",
            usage_metadata=usage_metadata,
            response_metadata=response_metadata,
        )
        return ChatResult(
            generations=[ChatGeneration(message=message)],
            llm_output={
                "token_usage": token_usage,
                "model_name": response_metadata["model_name"],
            },
        )

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        litellm = _import_litellm()
        response = litellm.completion(
            **self._completion_params(messages, stop, **kwargs)
        )
        return self._create_chat_result(response)

    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        litellm = _import_litellm()
        response = await litellm.acompletion(
            **self._completion_params(messages, stop, **kwargs)
        )
        return self._create_chat_result(response)
