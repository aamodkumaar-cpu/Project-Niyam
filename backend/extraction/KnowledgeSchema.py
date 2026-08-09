"""
Knowledge Schema.

Purpose:
    Defines the JSON contract expected from the knowledge extraction LLM.

Responsibilities:
    - Define the extraction JSON schema.
    - Ensure the LLM returns atomic source-grounded facts.
    - Keep the LLM output contract aligned with KnowledgeFactJson.

Does NOT:
    - Extract knowledge.
    - Validate facts against documents.
    - Call the LLM.
"""

from typing import Any


class KnowledgeSchema:
    """Defines the JSON schema for knowledge extraction."""

    def json_schema(self) -> dict[str, Any]:
        """Return the JSON schema expected from the extraction LLM."""

        return {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                    },
                    "source_quote": {
                        "type": "string",
                    },
                    "confidence": {
                        "type": "number",
                    },
                },
                "required": [
                    "name",
                    "source_quote",
                    "confidence",
                ],
                "additionalProperties": False,
            },
        }