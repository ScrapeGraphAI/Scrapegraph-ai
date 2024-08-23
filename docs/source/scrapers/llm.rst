.. _llm:

LLM
===

We support many known LLM models and providers used to analyze the web pages and extract the information requested by the user. Models can be split in **Chat Models** and **Embedding Models** (the latter are mainly used for Retrieval Augmented Generation RAG).
These models are specified inside the graph configuration dictionary and can be used interchangeably, for example by defining a different model for llm and embeddings.

- **Local Models**: These models are hosted on the local machine and can be used without any API key.
- **API-based Models**: These models are hosted on the cloud and require an API key to access them (eg. OpenAI, Groq, etc).

.. note::

    If the emebedding model is not specified, the library will use the default one for that LLM, if available.

Local Models
------------

Currently, local models are supported through Ollama integration. Ollama is a provider of LLM models which can be downloaded from here `Ollama <https://ollama.com/>`_.
Let's say we want to use **llama3** as chat model and **nomic-embed-text** as embedding model. We first need to pull them from ollama using:

.. code-block:: bash

   ollama pull llama3
   ollama pull nomic-embed-text

Then we can use them in the graph configuration as follows:

.. code-block:: python

    graph_config = {
        "llm": {
            "model": "llama3",
            "temperature": 0.0,
            "format": "json",
        },
        "embeddings": {
            "model": "nomic-embed-text",
        },
    }

You can also specify the **base_url** parameter to specify the models endpoint. By default, it is set to http://localhost:11434. This is useful if you are running Ollama on a Docker container or on a different machine.

If you want to host Ollama in a Docker container, you can use the following command:

.. code-block:: bash

    docker-compose up -d
    docker exec -it ollama ollama pull llama3

API-based Models
----------------

OpenAI
^^^^^^

You can get the API key from `here <https://platform.openai.com/api-keys>`_.

.. code-block:: python

    graph_config = {
        "llm": {
            "api_key": "OPENAI_API_KEY",
            "model": "gpt-3.5-turbo",
        },
    }

If you want to use text to speech models, you can specify the `tts_model` parameter:

.. code-block:: python

    graph_config = {
        "llm": {
            "api_key": "OPENAI_API_KEY",
            "model": "gpt-3.5-turbo",
            "temperature": 0.7,
        },
        "tts_model": {
            "api_key": "OPENAI_API_KEY",
            "model": "tts-1",
            "voice": "alloy"
        },
    }

Gemini
^^^^^^

You can get the API key from `here <https://ai.google.dev/gemini-api/docs/api-key>`_.

**Note**: some countries are not supported and therefore it won't be possible to request an API key. A possible workaround is to use a VPN or run the library on Colab.

.. code-block:: python

    graph_config = {
        "llm": {
            "api_key": "GEMINI_API_KEY",
            "model": "gemini-pro"
        },
    }

Groq
^^^^

You can get the API key from `here <https://console.groq.com/keys>`_. Groq doesn't support embedding models, so in the following example we are using Ollama one.

.. code-block:: python

    graph_config = {
        "llm": {
            "model": "groq/gemma-7b-it",
            "api_key": "GROQ_API_KEY",
            "temperature": 0
        },
        "embeddings": {
            "model": "ollama/nomic-embed-text",
        },
    }

Azure
^^^^^

We can also pass a model instance for the chat model and the embedding model. For Azure, a possible configuration would be:

.. code-block:: python

    llm_model_instance = AzureChatOpenAI(
        openai_api_version="AZURE_OPENAI_API_VERSION",
        azure_deployment="AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"
    )

    embedder_model_instance = AzureOpenAIEmbeddings(
        azure_deployment="AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT_NAME",
        openai_api_version="AZURE_OPENAI_API_VERSION",
    )
    # Supposing model_tokens are 100K
    model_tokens_count = 100000 
    graph_config = {
        "llm": {
            "model_instance": llm_model_instance,
            "model_tokens": model_tokens_count, 
        },
        "embeddings": {
            "model_instance": embedder_model_instance
        }
    }

Hugging Face Hub
^^^^^^^^^^^^^^^^

We can also pass a model instance for the chat model and the embedding model. For Hugging Face, a possible configuration would be:

.. code-block:: python

    llm_model_instance = HuggingFaceEndpoint(
        repo_id="mistralai/Mistral-7B-Instruct-v0.2",
        max_length=128,
        temperature=0.5,
        token="HUGGINGFACEHUB_API_TOKEN"
    )

    embedder_model_instance = HuggingFaceInferenceAPIEmbeddings(
        api_key="HUGGINGFACEHUB_API_TOKEN",
        model_name="sentence-transformers/all-MiniLM-l6-v2"
    )

    graph_config = {
        "llm": {
            "model_instance": llm_model_instance
        },
        "embeddings": {
            "model_instance": embedder_model_instance
        }
    }

Anthropic
^^^^^^^^^

We can also pass a model instance for the chat model and the embedding model. For Anthropic, a possible configuration would be:

.. code-block:: python

    embedder_model_instance = HuggingFaceInferenceAPIEmbeddings(
        api_key="HUGGINGFACEHUB_API_TOKEN",
        model_name="sentence-transformers/all-MiniLM-l6-v2"
    )

    graph_config = {
        "llm": {
            "api_key": "ANTHROPIC_API_KEY",
            "model": "claude-3-haiku-20240307",
            "max_tokens": 4000
        },
        "embeddings": {
            "model_instance": embedder_model_instance
        }
    }

Other LLM models
^^^^^^^^^^^^^^^^

We can also pass a model instance for the chat model and the embedding model through the **model_instance** parameter. 
This feature enables you to utilize a Langchain model instance.
You will discover the model you require within the provided list:

- `chat model list <https://python.langchain.com/v0.2/docs/integrations/chat/#all-chat-models>`_
- `embedding model list <https://python.langchain.com/v0.2/docs/integrations/text_embedding/#all-embedding-models>`_.

For instance, consider **chat model** Moonshot. We can integrate it in the following manner:

.. code-block:: python
    
    from langchain_community.chat_models.moonshot import MoonshotChat

    # The configuration parameters are contingent upon the specific model you select
    llm_instance_config = {
        "model": "moonshot-v1-8k",
        "base_url": "https://api.moonshot.cn/v1",
        "moonshot_api_key": "MOONSHOT_API_KEY",
    }

    llm_model_instance = MoonshotChat(**llm_instance_config)
    graph_config = {
        "llm": {
            "model_instance": llm_model_instance, 
            "model_tokens": 5000
        },
    }
    