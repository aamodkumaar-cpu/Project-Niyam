"""
Knowledge Schema.

Purpose:
    Defines the JSON contract expected from the knowledge extraction LLM.

Responsibilities:
    - Require the LLM to select deterministic source candidates.
    - Prevent the LLM from generating source evidence.

Does NOT:
    - Extract knowledge.
    - Validate facts against documents.
    - Call the LLM.
"""

from typing import Any


class KnowledgeSchema:
    """Defines the candidate-selection JSON schema."""

    def json_schema(self) -> dict[str, Any]:
        """Return the JSON schema expected from the extraction LLM."""

        return {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "candidate_id": {
                        "type": "string",
                    },
                    "confidence": {
                        "type": "number",
                    },
                },
                "required": [
                    "candidate_id",
                    "confidence",
                ],
                "additionalProperties": False,
            },
        }