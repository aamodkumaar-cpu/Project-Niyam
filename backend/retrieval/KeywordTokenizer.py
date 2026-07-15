"""
Keyword Tokenizer.

Purpose:
    Converts text into searchable keywords.

Responsibilities:
    - Lowercase text
    - Remove punctuation
    - Split into words

Does NOT:
    - Perform retrieval
    - Rank results
    - Generate embeddings
"""

import re


class KeywordTokenizer:

    def tokenize(
        self,
        text: str
    ) -> list[str]:

        text = text.lower()

        text = re.sub(
            r"[^a-z0-9\s]",
            " ",
            text
        )

        return text.split()