"""
Models token 
"""

models_tokens = {
    "openai": {
        "gpt-3.5-turbo-0125": 16385,
        "gpt-3.5-turbo": 4096,
        "gpt-3.5-turbo-1106": 16385,
        "gpt-3.5-turbo-instruct": 4096,
        "gpt-4-0125-preview": 128000,
        "gpt-4-turbo-preview": 128000,
        "gpt-4-turbo": 128000,
        "gpt-4-turbo-2024-04-09": 128000,
        "gpt-4-1106-preview": 128000,
        "gpt-4-vision-preview": 128000,
        "gpt-4": 8192,
        "gpt-4-0613": 8192,
        "gpt-4-32k": 32768,
        "gpt-4-32k-0613": 32768,
    },
    "azure": {
        "gpt-3.5-turbo": 4096,
        "gpt-4": 8192,
        "gpt-4-32k": 32768
    },
    "gemini": {
        "gemini-pro": 128000,
        "models/embedding-001": 2048
    },

    "ollama": {
        "llama2": 4096,
        "llama3": 8192,
        "mistral": 8192,
        "codellama": 16000,
        "dolphin-mixtral": 32000,
        "mistral-openorca": 32000,
        "stablelm-zephyr": 8192,
        "nomic-embed-text":8192
    },
    "groq": {
        "llama3-8b-8192": 8192,
        "llama3-70b-8192": 8192,
        "mixtral-8x7b-32768": 32768,
        "gemma-7b-it": 8192,
    },
    "claude": {
        "claude_instant": 100000,
        "claude2": 9000,
        "claude2.1": 200000,
        "claude3": 200000
    },
    "bedrock": {
        "anthropic.claude-3-haiku-20240307-v1:0": 200000,
        "anthropic.claude-3-sonnet-20240229-v1:0": 200000,
        "anthropic.claude-3-opus-20240229-v1:0": 200000,
        "anthropic.claude-v2:1": 200000,
        "anthropic.claude-v2": 100000,
        "anthropic.claude-instant-v1": 100000,
        "meta.llama3-8b-instruct-v1:0": 8192,
        "meta.llama3-70b-instruct-v1:0": 8192,
        "meta.llama2-13b-chat-v1": 4096,
        "meta.llama2-70b-chat-v1": 4096,
        "mistral.mistral-7b-instruct-v0:2": 32768,
        "mistral.mixtral-8x7b-instruct-v0:1": 32768,
        "mistral.mistral-large-2402-v1:0": 32768,
        "cohere.embed-english-v3": 512,
        "cohere.embed-multilingual-v3": 512
    },
    "mistral": {
        "mistralai/Mistral-7B-Instruct-v0.2": 32000
    }
}
