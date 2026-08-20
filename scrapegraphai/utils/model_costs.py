"""
Cost for 1k tokens in input
"""

MODEL_COST_PER_1K_TOKENS_INPUT = {
    ### MistralAI
    # General Purpose
    "open-mistral-nemo": 0.00015,
    "open-mistral-nemo-2407": 0.00015,
    "mistral-large": 0.002,
    "mistral-large-2407": 0.002,
    "mistral-small": 0.0002,
    "mistral-small-2409": 0.0002,
    # Specialist Models
    "codestral": 0.0002,
    "codestral-2405": 0.0002,
    "pixtral-12b": 0.00015,
    "pixtral-12b-2409": 0.00015,
    # Legacy Models
    "open-mistral-7b": 0.00025,
    "open-mixtral-8x7b": 0.0007,
    "open-mixtral-8x22b": 0.002,
    "mistral-small-latest": 0.001,
    "mistral-medium-latest": 0.00275,
    ### Bedrock - not Claude
    # AI21 Labs
    "a121.ju-ultra-v1": 0.0188,
    "a121.ju-mid-v1": 0.0125,
    "ai21.jamba-instruct-v1:0": 0.0005,
    # Meta - LLama
    "meta.llama2-13b-chat-v1": 0.00075,
    "meta.llama2-70b-chat-v1": 0.00195,
    "meta.llama3-8b-instruct-v1:0": 0.0003,
    "meta.llama3-70b-instruct-v1:0": 0.00265,
    "meta.llama3-1-8b-instruct-v1:0": 0.00022,
    "meta.llama3-1-70b-instruct-v1:0": 0.00099,
    "meta.llama3-1-405b-instruct-v1:0": 0.00532,
    # Cohere - Command
    "cohere.command-text-v14": 0.0015,
    "cohere.command-light-text-v14": 0.0003,
    "cohere.command-r-v1:0": 0.0005,
    "cohere.command-r-plus-v1:0": 0.003,
    # Mistral
    "mistral.mistral-7b-instruct-v0:2": 0.00015,
    "mistral.mistral-large-2402-v1:0": 0.004,
    "mistral.mistral-large-2407-v1:0": 0.002,
    "mistral.mistral-small-2402-v1:0": 0.001,
    "mistral.mixtral-7x8b-instruct-v0:1": 0.00045,
    # Amazon - Titan
    "amazon.titan-text-express-v1": 0.0002,
    "amazon.titan-text-lite-v1": 0.00015,
    "amazon.titan-text-premier-v1:0": 0.0005,
    "MiniMax-M2.7": 0.0003,
}

"""
Cost for 1k tokens in output
"""
MODEL_COST_PER_1K_TOKENS_OUTPUT = {
    # General Purpose
    "open-mistral-nemo": 0.00015,
    "open-mistral-nemo-2407": 0.00015,
    "mistral-large": 0.002,
    "mistral-large-2407": 0.006,
    "mistral-small": 0.0002,
    "mistral-small-2409": 0.0006,
    # Specialist Models
    "codestral": 0.0006,
    "codestral-2405": 0.0006,
    "pixtral-12b": 0.00015,
    "pixtral-12b-2409": 0.0006,
    # Legacy Models
    "open-mistral-7b": 0.00025,
    "open-mixtral-8x7b": 0.0007,
    "open-mixtral-8x22b": 0.006,
    "mistral-small-latest": 0.003,
    "mistral-medium-latest": 0.0081,
    ### Bedrock - not Claude
    # AI21 Labs
    "a121.ju-ultra-v1": 0.0188,
    "a121.ju-mid-v1": 0.0125,
    "ai21.jamba-instruct-v1:0": 0.0007,
    # Meta - LLama
    "meta.llama2-13b-chat-v1": 0.001,
    "meta.llama2-70b-chat-v1": 0.00256,
    "meta.llama3-8b-instruct-v1:0": 0.0006,
    "meta.llama3-70b-instruct-v1:0": 0.0035,
    "meta.llama3-1-8b-instruct-v1:0": 0.00022,
    "meta.llama3-1-70b-instruct-v1:0": 0.00099,
    "meta.llama3-1-405b-instruct-v1:0": 0.016,
    # Cohere - Command
    "cohere.command-text-v14": 0.002,
    "cohere.command-light-text-v14": 0.0006,
    "cohere.command-r-v1:0": 0.0015,
    "cohere.command-r-plus-v1:0": 0.015,
    # Mistral
    "mistral.mistral-7b-instruct-v0:2": 0.0002,
    "mistral.mistral-large-2402-v1:0": 0.012,
    "mistral.mistral-large-2407-v1:0": 0.006,
    "mistral.mistral-small-2402-v1:0": 0.003,
    "mistral.mixtral-7x8b-instruct-v0:1": 0.0007,
    # Amazon - Titan
    "amazon.titan-text-express-v1": 0.0006,
    "amazon.titan-text-lite-v1": 0.0002,
    "amazon.titan-text-premier-v1:0": 0.0015,
    "MiniMax-M2.7": 0.0012,
}


MODEL_CACHE_COST_PER_1K_TOKENS = {
    "MiniMax-M2.7": {"read": 0.00006, "write": 0.000375},
}


MODEL_COST_TIERS_PER_1K_TOKENS = {
    "MiniMax-M3": {
        "standard": (
            {
                "input_tokens_lte": 512000,
                "input": 0.0003,
                "output": 0.0012,
                "cache_read": 0.00006,
                "cache_write": None,
            },
            {
                "input_tokens_gt": 512000,
                "input": 0.0006,
                "output": 0.0024,
                "cache_read": 0.00012,
                "cache_write": None,
            },
        ),
        "priority": (
            {
                "input_tokens_lte": 512000,
                "input": 0.00045,
                "output": 0.0018,
                "cache_read": 0.00009,
                "cache_write": None,
            },
            {
                "input_tokens_gt": 512000,
                "input": 0.0009,
                "output": 0.0036,
                "cache_read": 0.00018,
                "cache_write": None,
            },
        ),
    }
}


def get_model_cost_per_1k_tokens(
    model_name: str,
    input_tokens: int,
    is_completion: bool = False,
    service_tier: str = "standard",
) -> float:
    """Return the applicable input or output rate for a model."""
    if input_tokens < 0:
        raise ValueError("input_tokens must not be negative")

    if model_name in MODEL_COST_TIERS_PER_1K_TOKENS:
        try:
            pricing_tiers = MODEL_COST_TIERS_PER_1K_TOKENS[model_name][service_tier]
        except KeyError as exc:
            raise ValueError(
                f"Unsupported service tier {service_tier!r} for {model_name}"
            ) from exc

        rate_key = "output" if is_completion else "input"
        for pricing in pricing_tiers:
            upper_bound = pricing.get("input_tokens_lte")
            lower_bound = pricing.get("input_tokens_gt")
            if upper_bound is not None and input_tokens <= upper_bound:
                return float(pricing[rate_key])
            if lower_bound is not None and input_tokens > lower_bound:
                return float(pricing[rate_key])
        raise ValueError(f"No pricing tier matches {input_tokens} input tokens")

    costs = (
        MODEL_COST_PER_1K_TOKENS_OUTPUT
        if is_completion
        else MODEL_COST_PER_1K_TOKENS_INPUT
    )
    return costs[model_name]
