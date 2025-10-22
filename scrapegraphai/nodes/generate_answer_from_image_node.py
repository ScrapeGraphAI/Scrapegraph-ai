"""
GenerateAnswerFromImageNode Module
"""

import asyncio
import base64
from typing import List, Optional

import aiohttp

from .base_node import BaseNode


class GenerateAnswerFromImageNode(BaseNode):
    """
    GenerateAnswerFromImageNode analyzes images from the state dictionary using the OpenAI API
    and updates the state with the consolidated answers.
    """

    def __init__(
        self,
        input: str,
        output: List[str],
        node_config: Optional[dict] = None,
        node_name: str = "GenerateAnswerFromImageNode",
    ):
        super().__init__(node_name, "node", input, output, 2, node_config)

    async def process_image(self, session, api_key, image_data, user_prompt):
        """
        async process image
        """
        base64_image = base64.b64encode(image_data).decode("utf-8")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        # Get max_tokens from config, default to 4000 for better extraction
        max_tokens = self.node_config.get("config", {}).get("llm", {}).get("max_tokens", 4000)

        # Strip provider prefix (e.g., "openai/gpt-4o" -> "gpt-4o")
        model = self.node_config["config"]["llm"]["model"]
        if "/" in model:
            model = model.split("/", 1)[1]

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
            "max_tokens": max_tokens,
        }

        async with session.post(
            "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
        ) as response:
            result = await response.json()

            # Better error handling
            if "error" in result:
                error_msg = result.get("error", {}).get("message", "Unknown error")
                print(f"⚠️  OpenAI API Error: {error_msg}")
                return f"API Error: {error_msg}"

            content = (
                result.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "No response")
            )

            if not content or content == "No response":
                print(f"⚠️  Empty response from OpenAI. Full result: {result}")

            return content

    async def execute_async(self, state: dict) -> dict:
        """
        Processes images from the state, generates answers,
        consolidates the results, and updates the state asynchronously.
        """
        self.logger.info(f"--- Executing {self.node_name} Node ---")

        images = state.get("screenshots", [])
        analyses = []

        supported_models = ("gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4")

        if (
            self.node_config["config"]["llm"]["model"].split("/")[-1]
            not in supported_models
        ):
            raise ValueError(
                f"""The model provided
                             is not supported. Supported models are:
                             {", ".join(supported_models)}."""
            )

        api_key = self.node_config.get("config", {}).get("llm", {}).get("api_key", "")

        async with aiohttp.ClientSession() as session:
            tasks = [
                self.process_image(
                    session,
                    api_key,
                    image_data,
                    state.get("user_prompt", "Extract information from the image"),
                )
                for image_data in images
            ]

            analyses = await asyncio.gather(*tasks)

        consolidated_analysis = " ".join(analyses)

        state["answer"] = {"consolidated_analysis": consolidated_analysis}

        return state

    def execute(self, state: dict) -> dict:
        """
        Wrapper to run the asynchronous execute_async function in a synchronous context.
        """
        try:
            eventloop = asyncio.get_event_loop()
        except RuntimeError:
            eventloop = None

        if eventloop and eventloop.is_running():
            task = eventloop.create_task(self.execute_async(state))
            state = eventloop.run_until_complete(asyncio.gather(task))[0]
        else:
            state = asyncio.run(self.execute_async(state))

        return state
