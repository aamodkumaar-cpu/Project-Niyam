"""
Evidence Selection Safety Gate.

Type:
    Domain Service

Purpose:
    Prevent explicitly scoped questions from passing candidates whose
    structural evidence belongs to a conflicting scope.

Responsibilities:
    - Detect explicit named scope expressed in a question.
    - Compare requested scope with candidate structural evidence.
    - Reject candidates that clearly conflict with the requested scope.
    - Preserve candidates when no explicit scope can be established.

Does NOT:
    - Retrieve knowledge.
    - Rank candidates.
    - Interpret facts.
    - Call the LLM.
    - Generate answers.
    - Maintain domain-specific entity lists.
"""

from __future__ import annotations

import re

from backend.extraction.ExtractionCandidate import ExtractionCandidate
from backend.retrieval.KeywordTokenizer import KeywordTokenizer


class EvidenceSelectionSafetyGate:
    """Filter extraction candidates that conflict with explicit question scope."""

    _SCOPE_PATTERN = re.compile(
        r"""
        \b
        (?:
            at
            |with
            |from
            |for
            |under
            |within
            |during
        )
        \s+
        (?!all\b)
        (?!each\b)
        (?!every\b)
        (?!any\b)
        (
            [A-Za-z0-9][A-Za-z0-9&@._\[\]/+#-]*
            (?:
                \s+
                [A-Za-z0-9][A-Za-z0-9&@._\[\]/+#-]*
            ){0,4}
        )
        """,
        flags=re.IGNORECASE | re.VERBOSE,
    )

    _GENERIC_SCOPE_TERMS = {
        "company",
        "companies",
        "role",
        "roles",
        "position",
        "positions",
        "document",
        "documents",
        "source",
        "sources",
        "item",
        "items",
        "heading",
        "headings",
        "experience",
        "experiences",
        "land",
        "earth",
        "world",
        "industry",
        "industries",
        "business",
        "businesses",
        "organization",
        "organizations",
        "team",
        "teams",
        "department",
        "departments",
    }

    _SCOPE_STOP_WORDS = {
        "the",
        "a",
        "an",
        "my",
        "your",
        "our",
        "their",
        "his",
        "her",
        "this",
        "that",
        "these",
        "those",
        "all",
        "each",
        "every",
        "any",
    }

    def __init__(
        self,
        keyword_tokenizer: KeywordTokenizer,
    ) -> None:
        """Initialize the evidence selection safety gate."""

        self.keyword_tokenizer = keyword_tokenizer

    def filter(
        self,
        question: str,
        candidates: list[ExtractionCandidate],
    ) -> list[ExtractionCandidate]:
        """Return candidates that are safe for the explicitly requested scope."""

        if not candidates:
            return []

        scope_tokens = self._extract_scope_tokens(
            question
        )

        if not scope_tokens:
            return candidates

        return [
            candidate
            for candidate in candidates
            if self._is_scope_compatible(
                scope_tokens=scope_tokens,
                candidate=candidate,
            )
        ]

    def _extract_scope_tokens(
        self,
        question: str,
    ) -> list[str]:
        """Extract meaningful explicit scope tokens from the question."""

        matches = self._SCOPE_PATTERN.findall(
            question
        )

        if not matches:
            return []

        for scope_text in reversed(matches):
            tokens = self._meaningful_tokens(
                scope_text
            )

            if not tokens:
                continue

            if all(
                token in self._GENERIC_SCOPE_TERMS
                for token in tokens
            ):
                continue

            if all(
                token in self._SCOPE_STOP_WORDS
                or token in self._GENERIC_SCOPE_TERMS
                for token in tokens
            ):
                continue

            return tokens

        return []

    def _is_scope_compatible(
        self,
        scope_tokens: list[str],
        candidate: ExtractionCandidate,
    ) -> bool:
        """Return whether candidate structural evidence matches requested scope."""

        structural_text = " ".join(
            part
            for part in (
                candidate.heading,
                candidate.structural_context,
            )
            if part
        )

        structural_tokens = set(
            self._meaningful_tokens(
                structural_text
            )
        )

        if not structural_tokens:
            return False

        return all(
            token in structural_tokens
            for token in scope_tokens
        )

    def _meaningful_tokens(
        self,
        text: str,
    ) -> list[str]:
        """Return normalized meaningful tokens from text."""

        tokens = self.keyword_tokenizer.tokenize(
            text.lower()
        )

        return [
            token
            for token in tokens
            if len(token) >= 2
        ]