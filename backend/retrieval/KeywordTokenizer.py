"""
Keyword Tokenizer.

Type:
    Domain Service

Purpose:
    Converts user text into normalized search tokens.

Responsibilities:
    - Normalize text.
    - Remove punctuation.
    - Tokenize into searchable words.
    - Remove duplicate tokens while preserving order.

Does NOT:
    - Perform retrieval.
    - Rank results.
    - Generate embeddings.
    - Remove stop words.
"""

import re


class KeywordTokenizer:
    """Converts text into normalized search tokens."""

    def tokenize(
        self,
        text: str
    ) -> list[str]:
        """Return normalized search tokens."""

        normalized = re.sub(
            r"[^a-z0-9\s]",
            " ",
            text.lower()
        )

        tokens = normalized.split()

        return list(dict.fromkeys(tokens))