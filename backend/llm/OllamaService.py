"""
Ollama Service.

Purpose:
    Communicates with the Ollama server.

Responsibilities:
    - Send chat messages to the configured model
    - Return the generated response

Does NOT:
    - Build prompts
    - Retrieve documents
    - Format responses
"""

from ollama import chat
from backend.config.settings import OLLAMA_MODEL


class OllamaService:

    def generate(
        self,
        messages: list[dict]
    ) -> str:

        response = chat(
            model=OLLAMA_MODEL,
            messages=messages
        )

        return response["message"]["content"]