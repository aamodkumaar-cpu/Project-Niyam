"""
Question Normalizer.

Type:
    Domain Service

Purpose:
    Normalizes user questions before retrieval.

Responsibilities:
    - Convert to lowercase
    - Remove punctuation
    - Remove common stop words
    - Normalize whitespace

Does NOT:
    - Rewrite questions
    - Expand synonyms
    - Retrieve knowledge
    - Call the LLM
"""

import re
from typing import Final


class QuestionNormalizer:
    """Normalizes user questions."""

    _POSSESSIVE_PATTERN: Final[str] = r"'s\b"
    _WORD_SEPARATOR_PATTERN: Final[str] = r"[^\w\s]"

    _STOP_WORDS: Final[frozenset[str]] = frozenset({
        "a",
        "an",
        "the",
        "is",
        "are",
        "was",
        "were",
        "to",
        "of",
        "for",
        "from",
        "with",
        "and",
        "or",
        "in",
        "on",
        "at",
        "by",
        "into",
        "about",
        "please",
        "can",
        "could",
        "would",
        "should",
        "will",
        "may",
        "me",
        "my",
        "your",
        "their",
        "our",
        "help",
        "show",
        "share",
        "tell",
        "give",
        "list"
    })

    def normalize(
        self,
        question: str
    ) -> str:
        """Normalize the user question."""

        question = question.lower()

        question = re.sub(
            self._POSSESSIVE_PATTERN,
            "",
            question
        )

        question = re.sub(
            self._WORD_SEPARATOR_PATTERN,
            " ",
            question
        )

        words = [
            word
            for word in question.split()
            if word not in self._STOP_WORDS
        ]

        return " ".join(words)