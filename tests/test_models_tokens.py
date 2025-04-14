from scrapegraphai.helpers.models_tokens import models_tokens


class TestModelsTokens:
    """Test suite for verifying the models_tokens dictionary content and structure."""

    def test_openai_tokens(self):
        """Test that the 'openai' provider exists and its tokens are valid positive integers."""
        openai_models = models_tokens.get("openai")
        assert openai_models is not None, (
            "'openai' key should be present in models_tokens"
        )
        for model, token in openai_models.items():
            assert isinstance(model, str), "Model name should be a string"
            assert isinstance(token, int), "Token limit should be an integer"
            assert token > 0, "Token limit should be positive"

    def test_azure_openai_tokens(self):
        """Test that the 'azure_openai' provider exists and its tokens are valid."""
        azure_models = models_tokens.get("azure_openai")
        assert azure_models is not None, "'azure_openai' key should be present"
        for model, token in azure_models.items():
            assert isinstance(model, str), "Model name should be a string"
            assert isinstance(token, int), "Token limit should be an integer"

    def test_google_providers(self):
        """Test that Google provider dictionaries ('google_genai' and 'google_vertexai') contain expected entries."""
        google_genai = models_tokens.get("google_genai")
        google_vertexai = models_tokens.get("google_vertexai")
        assert google_genai is not None, "'google_genai' key should be present"
        assert google_vertexai is not None, "'google_vertexai' key should be present"
        # Check a specific key from google_genai
        assert "gemini-pro" in google_genai, (
            "'gemini-pro' should be in google_genai models"
        )
        # Validate token values types
        for provider in [google_genai, google_vertexai]:
            for token in provider.values():
                assert isinstance(token, int), "Token limit must be an integer"

    def test_non_existent_provider(self):
        """Test that a non-existent provider returns None."""
        assert models_tokens.get("non_existent") is None, (
            "Non-existent provider should return None"
        )

    def test_total_model_keys(self):
        """Test that the total number of models across all providers is above an expected count."""
        total_keys = sum(len(details) for details in models_tokens.values())
        assert total_keys > 20, "Expected more than 20 total model tokens defined"

    def test_specific_token_value(self):
        """Test specific expected token value for a known model."""
        openai = models_tokens.get("openai")
        # Verify that the token limit for "gpt-4" is 8192 as defined
        assert openai.get("gpt-4") == 8192, "Expected token limit for gpt-4 to be 8192"

    def test_non_empty_model_keys(self):
        """Ensure that model token names are non-empty strings."""
        for provider, model_dict in models_tokens.items():
            for model in model_dict.keys():
                assert model != "", (
                    f"Model name in provider '{provider}' should not be empty."
                )

    def test_token_limits_range(self):
        """Test that token limits for all models fall within a plausible range (e.g., 1 to 300000)."""
        for provider, model_dict in models_tokens.items():
            for model, token in model_dict.items():
                assert 1 <= token <= 1100000, (
                    f"Token limit for {model} in provider {provider} is out of plausible range."
                )

    def test_provider_structure(self):
        """Test that every provider in models_tokens has a dictionary as its value."""
        for provider, models in models_tokens.items():
            assert isinstance(models, dict), (
                f"Provider {provider} should map to a dictionary, got {type(models).__name__}"
            )

    def test_non_empty_provider(self):
        """Test that each provider dictionary is not empty."""
        for provider, models in models_tokens.items():
            assert len(models) > 0, (
                f"Provider {provider} should contain at least one model."
            )

    def test_specific_model_token_values(self):
        """Test specific expected token values for selected models from various providers."""
        # Verify a token for a selected model from the 'openai' provider
        openai = models_tokens.get("openai")
        assert openai.get("gpt-3.5-turbo-0125") == 16385, (
            "Expected token limit for gpt-3.5-turbo-0125 in openai to be 16385"
        )

        # Verify a token for a selected model from the 'azure_openai' provider
        azure = models_tokens.get("azure_openai")
        assert azure.get("gpt-3.5") == 4096, (
            "Expected token limit for gpt-3.5 in azure_openai to be 4096"
        )

        # Verify a token for a selected model from the 'anthropic' provider
        anthropic = models_tokens.get("anthropic")
        assert anthropic.get("claude_instant") == 100000, (
            "Expected token limit for claude_instant in anthropic to be 100000"
        )

    def test_providers_count(self):
        """Test that the total number of providers is as expected (at least 15)."""
        assert len(models_tokens) >= 15, (
            "Expected at least 15 providers in models_tokens"
        )

    def test_non_existent_model(self):
        """Test that a non-existent model within a valid provider returns None."""
        openai = models_tokens.get("openai")
        assert openai.get("non_existent_model") is None, (
            "Non-existent model should return None from a valid provider."
        )

    def test_no_whitespace_in_model_names(self):
        """Test that model names do not contain leading or trailing whitespace."""
        for provider, model_dict in models_tokens.items():
            for model in model_dict.keys():
                # Assert that stripping whitespace does not change the model name
                assert model == model.strip(), (
                    f"Model name '{model}' in provider '{provider}' contains leading or trailing whitespace."
                )

    def test_specific_models_additional(self):
        """Test specific token values for additional models across various providers."""
        # Check some models in the 'ollama' provider
        ollama = models_tokens.get("ollama")
        assert ollama.get("llama2") == 4096, (
            "Expected token limit for 'llama2' in ollama to be 4096"
        )
        assert ollama.get("llama2:70b") == 4096, (
            "Expected token limit for 'llama2:70b' in ollama to be 4096"
        )

        # Check a specific model from the 'mistralai' provider
        mistralai = models_tokens.get("mistralai")
        assert mistralai.get("open-codestral-mamba") == 256000, (
            "Expected token limit for 'open-codestral-mamba' in mistralai to be 256000"
        )

        # Check a specific model from the 'deepseek' provider
        deepseek = models_tokens.get("deepseek")
        assert deepseek.get("deepseek-chat") == 28672, (
            "Expected token limit for 'deepseek-chat' in deepseek to be 28672"
        )

        # Check a model from the 'ernie' provider
        ernie = models_tokens.get("ernie")
        assert ernie.get("ernie-bot") == 4096, (
            "Expected token limit for 'ernie-bot' in ernie to be 4096"
        )

    def test_nvidia_specific(self):
        """Test specific token value for 'meta/codellama-70b' in the nvidia provider."""
        nvidia = models_tokens.get("nvidia")
        assert nvidia is not None, "'nvidia' provider should exist"
        # Verify token for 'meta/codellama-70b' equals 16384 as defined in the nvidia dictionary
        assert nvidia.get("meta/codellama-70b") == 16384, (
            "Expected token limit for 'meta/codellama-70b' in nvidia to be 16384"
        )

    def test_groq_specific(self):
        """Test specific token value for 'claude-3-haiku-20240307\'' in the groq provider."""
        groq = models_tokens.get("groq")
        assert groq is not None, "'groq' provider should exist"
        # Note: The model name has an embedded apostrophe at the end in its name.
        assert groq.get("claude-3-haiku-20240307'") == 8192, (
            "Expected token limit for 'claude-3-haiku-20240307\\'' in groq to be 8192"
        )

    def test_togetherai_specific(self):
        """Test specific token value for 'meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo' in the toghetherai provider."""
        togetherai = models_tokens.get("toghetherai")
        assert togetherai is not None, "'toghetherai' provider should exist"
        expected = 128000
        model_name = "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo"
        assert togetherai.get(model_name) == expected, (
            f"Expected token limit for '{model_name}' in toghetherai to be {expected}"
        )

    def test_ernie_all_values(self):
        """Test that all models in the 'ernie' provider have token values exactly 4096."""
        ernie = models_tokens.get("ernie")
        assert ernie is not None, "'ernie' provider should exist"
        for model, token in ernie.items():
            assert token == 4096, (
                f"Expected token limit for '{model}' in ernie to be 4096, got {token}"
            )
