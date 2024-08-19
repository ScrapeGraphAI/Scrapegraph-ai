"""
generate answer from image module
"""
import base64
from typing import List, Optional
import requests
from .base_node import BaseNode
from ..utils.logging import get_logger

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

    def execute(self, state: dict) -> dict:
        """
        Processes images from the state, generates answers, 
        consolidates the results, and updates the state.
        """
        self.logger.info(f"--- Executing {self.node_name} Node ---")

        images = state.get('screenshots', [])
        analyses = []

        api_key = self.node_config.get("config", {}).get("llm", {}).get("api_key", "")

        supported_models = ("gpt-4o", "gpt-4o-mini", "gpt-4-turbo")

        if self.node_config["config"]["llm"]["model"] not in supported_models:
            raise ValueError(f"""Model '{self.node_config['config']['llm']['model']}'
                             is not supported. Supported models are: 
                             {', '.join(supported_models)}.""")

        if self.node_config["config"]["llm"]["model"].startswith("gpt"):
            for image_data in images:
                base64_image = base64.b64encode(image_data).decode('utf-8')

                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                }

                payload = {
                    "model": self.node_config["config"]["llm"]["model"],
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": state.get("user_prompt", 
                                                    "Extract information from the image")
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64_image}"
                                    }
                                }
                            ]
                        }
                    ],
                    "max_tokens": 300
                }

                response = requests.post("https://api.openai.com/v1/chat/completions",
                                        headers=headers,
                                        json=payload,
                                        timeout=10)
                result = response.json()

                response_text = result.get('choices',
                                        [{}])[0].get('message', {}).get('content', 'No response')
                analyses.append(response_text)

            consolidated_analysis = " ".join(analyses)

            state['answer'] = {
                "consolidated_analysis": consolidated_analysis
            }

            return state
