import pytest

from scrapegraphai.models.openai_tts import OpenAITextToSpeech


class FakeResponse:
    """Fake response object to simulate the API call return value."""

    def __init__(self, text):
        # Emulate audio conversion by prepending a fixed prefix to the input text.
        self.content = b"converted:" + text.encode()


class FakeSpeech:
    """Fake speech class with a create method that simulates generating speech."""

    def create(self, model, voice, input):
        # We ignore the model and voice for the fake implementation.
        return FakeResponse(input)


class FakeAudio:
    """Fake audio class that provides a speech attribute."""

    def __init__(self):
        self.speech = FakeSpeech()


class FakeClient:
    """Fake client to simulate OpenAI's audio API without making actual network calls."""

    def __init__(self):
        self.audio = FakeAudio()


@pytest.fixture
def tts_config():
    """Fixture for providing configuration for OpenAITextToSpeech."""
    return {"api_key": "dummy_key", "model": "custom-model", "voice": "custom_voice"}


@pytest.fixture
def tts_instance(tts_config):
    """Fixture for an OpenAITextToSpeech instance with a fake client to avoid external API calls."""
    tts = OpenAITextToSpeech(tts_config)
    # Override the client with our FakeClient.
    tts.client = FakeClient()
    return tts


def test_run_valid_text(tts_instance):
    """Test that run method returns the appropriate byte result for a valid text input."""
    input_text = "Hello, OpenAI!"
    result = tts_instance.run(input_text)
    # The expected response is the fake conversion with the prefix b"converted:".
    expected = b"converted:" + input_text.encode()
    assert result == expected


def test_run_empty_text(tts_instance):
    """Test that run method works correctly when provided with an empty string."""
    input_text = ""
    result = tts_instance.run(input_text)
    expected = b"converted:"  # b"converted:" + b"" is just b"converted:"
    assert result == expected


def test_attributes_set(tts_config):
    """Test that the OpenAITextToSpeech instance correctly sets attributes from the configuration."""
    tts = OpenAITextToSpeech(tts_config)
    # The model and voice should be set to the values provided in configuration.
    assert tts.model == tts_config["model"]
    assert tts.voice == tts_config["voice"]
    # The client should be an instance of OpenAI; check that it is not None.
    assert tts.client is not None


def test_default_config_no_model_voice():
    """Test that default values for model and voice are used when they are not provided in the configuration."""
    # Create a configuration without 'model' and 'voice' keys.
    config = {"api_key": "dummy_key"}
    tts = OpenAITextToSpeech(config)
    # Default values should be "tts-1" for model and "alloy" for voice.
    assert tts.model == "tts-1"
    assert tts.voice == "alloy"


def test_run_unicode_text(tts_instance):
    """Test that run method correctly handles Unicode characters in the input text."""
    input_text = "こんにちは、世界！"  # "Hello, World!" in Japanese.
    result = tts_instance.run(input_text)
    expected = b"converted:" + input_text.encode()
    assert result == expected


def test_run_non_string_input(tts_instance):
    """Test that run method raises an error when non-string input is provided."""
    with pytest.raises(AttributeError):
        # Passing an integer to run should fail when trying to call .encode() on a non-string type.
        tts_instance.run(123)


def test_run_exception(tts_instance):
    """Test that run method propagates exceptions from the client's API call."""

    def raise_exception(model, voice, input):
        raise Exception("API failure")

    tts_instance.client.audio.speech.create = raise_exception
    with pytest.raises(Exception, match="API failure"):
        tts_instance.run("Any text")


def test_run_long_text(tts_instance):
    """Test that run method correctly handles long text input."""
    long_text = "a" * 10000  # a string of 10,000 'a' characters
    result = tts_instance.run(long_text)
    expected = b"converted:" + long_text.encode()
    assert result == expected


def test_run_whitespace_text(tts_instance):
    """Test that run method correctly handles text that is only whitespace."""
    whitespace_text = "    \n\t  "
    result = tts_instance.run(whitespace_text)
    expected = b"converted:" + whitespace_text.encode()
    assert result == expected


def test_constructor_base_url_usage(tts_config, monkeypatch):
    """Test that OpenAITextToSpeech passes the base_url value from the configuration to the OpenAI client."""

    # Define a fake OpenAI class that captures the initialization parameters.
    class FakeOpenAI:
        def __init__(self, api_key, base_url=None):
            self.api_key = api_key
            self.base_url = base_url

        def __getattr__(self, name):
            # Return a dummy function for any method calls.
            return lambda *args, **kwargs: None

    # Ensure the configuration has a base_url.
    custom_url = "https://custom.api.openai.com"
    tts_config_with_url = tts_config.copy()
    tts_config_with_url["base_url"] = custom_url

    # Monkey-patch the OpenAI class in the module to use our FakeOpenAI.
    monkeypatch.setattr("scrapegraphai.models.openai_tts.OpenAI", FakeOpenAI)

    # Create an instance of OpenAITextToSpeech and check that the client has the expected base_url.
    from scrapegraphai.models.openai_tts import OpenAITextToSpeech

    tts = OpenAITextToSpeech(tts_config_with_url)
    assert hasattr(tts.client, "base_url")
    assert tts.client.base_url == custom_url


def test_run_response_no_content(tts_instance):
    """Test that run method raises AttributeError if the response from the API does not contain a 'content' attribute."""

    # Create a fake function that simulates a response missing the "content" attribute.
    def fake_create_no_content(model, voice, input):
        # Return an object with no content attribute.
        class NoContent:
            pass

        return NoContent()

    # Patch the fake client's speech.create method.
    tts_instance.client.audio.speech.create = fake_create_no_content

    with pytest.raises(AttributeError):
        tts_instance.run("Test text without content attribute")
