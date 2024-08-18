from typing import List, Optional
from .base_node import BaseNode
import base64
import requests

class GenerateAnswerFromImageNode(BaseNode):
    """
    GenerateAnswerFromImageNode analyzes images from the state dictionary using the OpenAI API
    and updates the state with the generated answers.
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
        """Processes images from the state, generates answers, and updates the state."""
        # Retrieve the image data from the state dictionary
        images = state.get('screenshots', [])
        results = []

        # OpenAI API Key
        for image_data in images:
            # Encode the image data to base64
            base64_image = base64.b64encode(image_data).decode('utf-8')

            # Prepare API request
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.node_config.get("config").get("llm").get("api_key")}"
            }

            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": state.get("user_prompt", "Extract information from the image")
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

            # Make the API request
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
            result = response.json()

            # Extract the response text
            response_text = result.get('choices', [{}])[0].get('message', {}).get('content', 'No response')

            # Append the result to the results list
            results.append({
                "analysis": response_text
            })

        # Update the state dictionary with the results
        state['answer'] = results
        return state
