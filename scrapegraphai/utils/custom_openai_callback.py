import threading
from contextlib import contextmanager
from langchain_community.callbacks import get_openai_callback

class CustomOpenAiCallbackManager:
    _lock = threading.Lock()

    @contextmanager
    def exclusive_get_openai_callback(self):
        if CustomOpenAiCallbackManager._lock.acquire(blocking=False):
            try:
                with get_openai_callback() as cb:
                    yield cb
            finally:
                CustomOpenAiCallbackManager._lock.release()
        else:
            yield None