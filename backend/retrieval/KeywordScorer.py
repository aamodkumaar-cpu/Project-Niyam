"""
Keyword Scorer.

Type:
    Domain Service

Purpose:
    Measures lexical coverage between query tokens and candidate tokens.

Responsibilities:
    - Calculate query-term coverage.
    - Produce a normalized lexical relevance score.
    - Treat each meaningful query token as an independent signal.
    - Keep scoring deterministic.

Does NOT:
    - Tokenize text.
    - Remove stop words.
    - Perform retrieval.
    - Perform semantic similarity.
    - Understand domain meaning.
    - Infer relationships between terms.
    - Rank candidates.
    - Call the LLM.
"""

from collections.abc import Sequence


class KeywordScorer:
    """Calculates normalized lexical coverage."""

    def score(
        self,
        query_tokens: Sequence[str],
        content_tokens: Sequence[str],
    ) -> float:
        """Return the proportion of query tokens found in the content."""

        if not query_tokens:
            return 0.0

        content_set = set(content_tokens)

        matched_tokens = {
            token
            for token in query_tokens
            if token in content_set
        }

        return len(matched_tokens) / len(
            set(query_tokens)
        )