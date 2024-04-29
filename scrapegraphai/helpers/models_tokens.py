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

    "gemini": {
        "gemini-pro": 128000,
    },

    "ollama": {
        "llama2": 4096,
        "llama3": 8192,
        "mistral": 8192,
        "codellama": 16000,
        "dolphin-mixtral": 32000,
        "mistral-openorca": 32000,
        "stablelm-zephyr": 8192
    },
    "gemma": {
        "gemma:2b": 8192,
        "gemma:7b": 8192
    }
}
