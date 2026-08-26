"""
Keyword Tokenizer.

Type:

    Domain Service

Purpose:

    Converts user text into normalized search tokens.

Responsibilities:

    - Normalize text.
    - Preserve meaningful identifier punctuation.
    - Tokenize into searchable words and identifiers.
    - Remove duplicate tokens while preserving order.

Does NOT:

    - Perform retrieval.
    - Rank results.
    - Generate embeddings.
    - Remove stop words.
"""

from __future__ import annotations

import re


class KeywordTokenizer:
    """Converts text into normalized search tokens."""

    _TOKEN_PATTERN = re.compile(
        r"\d+\[\d+\](?:\.[a-z0-9]+)?"
        r"|[a-z0-9]+(?:[._/\-][a-z0-9]+)*",
        re.IGNORECASE,
    )

    def tokenize(
        self,
        text: str,
    ) -> list[str]:
        """Return normalized search tokens."""

        normalized = text.lower()

        tokens: list[str] = []

        for match in self._TOKEN_PATTERN.finditer(
            normalized
        ):
            token = match.group(0)

            tokens.append(token)

            parts = re.split(
                r"[._/\[\]-]+",
                token,
            )

            tokens.extend(
                part
                for part in parts
                if part
            )

        return list(
            dict.fromkeys(
                tokens
            )
        )