"""
Event loop helper module
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor


def run_coroutine_sync(coro):
    """
    Runs a coroutine from synchronous code.

    Uses asyncio.run() when the current thread has no running event loop.
    When called from code that already has one (Jupyter, FastAPI, and
    similar environments), the coroutine runs on its own loop in a worker
    thread, since asyncio.run() and loop.run_until_complete() both raise
    RuntimeError in that case.

    Args:
        coro: The coroutine to execute.

    Returns:
        The value returned by the coroutine.
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    with ThreadPoolExecutor(max_workers=1) as executor:
        return executor.submit(asyncio.run, coro).result()
