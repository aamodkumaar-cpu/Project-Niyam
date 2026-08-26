"""
Ollama Service.

Purpose:
Communicates with the Ollama server.

Responsibilities:
- Send chat messages to the configured model
- Return the generated response
- Support optional structured output format

Does NOT:
- Build prompts
- Retrieve documents
- Format responses
"""

from typing import Literal, cast

from pydantic.json_schema import JsonSchemaValue
from ollama import chat

from backend.config.settings import OLLAMA_MODEL
from backend.llm.Message import Messages


class OllamaService:
    """Client for the configured LLM."""

    def generate(
        self,
        messages: Messages,
        response_format: (
            JsonSchemaValue
            | Literal["", "json"]
            | None
        ) = None
    ) -> str:
        """Generate a response from the configured LLM."""

        response = chat(
            model=OLLAMA_MODEL,
            messages=messages,
            format=response_format,
            options={
                "temperature": 0,
            },
        )

        content = cast(
            str,
            response["message"]["content"]
        )

        return content