"""
Extraction Candidate Ranker.

Type:

    Domain Service

Purpose:

    Rank extraction candidates using deterministic lexical evidence and
    select a bounded evidence set for LLM processing.

Responsibilities:

    - Calculate candidate-level lexical relevance.
    - Include structural scope when calculating relevance.
    - Rank candidates deterministically.
    - Retain candidates with meaningful relative relevance.
    - Bound the number of candidates sent to the LLM.

Does NOT:

    - Call the LLM.
    - Interpret facts.
    - Validate source evidence.
    - Generate answers.
"""

from __future__ import annotations

from backend.extraction.ExtractionCandidate import ExtractionCandidate
from backend.retrieval.KeywordScorer import KeywordScorer
from backend.retrieval.KeywordTokenizer import KeywordTokenizer


class ExtractionCandidateRanker:
    """Rank extraction candidates using deterministic lexical relevance."""

    _KEYWORD_STOP_WORDS: frozenset[str] = frozenset(
        {
            "a",
            "an",
            "and",
            "are",
            "as",
            "at",
            "be",
            "by",
            "for",
            "from",
            "how",
            "in",
            "is",
            "it",
            "of",
            "on",
            "or",
            "that",
            "the",
            "their",
            "this",
            "to",
            "what",
            "when",
            "where",
            "which",
            "who",
            "why",
            "with",
            "each",
            "other",
            "associated",
        }
    )

    def __init__(
        self,
        keyword_tokenizer: KeywordTokenizer,
        keyword_scorer: KeywordScorer,
        maximum_candidates: int = 20,
        minimum_relative_score: float = 0.50,
    ) -> None:
        """Initialize the extraction candidate ranker."""

        self.keyword_tokenizer = keyword_tokenizer
        self.keyword_scorer = keyword_scorer
        self.maximum_candidates = maximum_candidates
        self.minimum_relative_score = (
            minimum_relative_score
        )

    def rank(
        self,
        question: str,
        candidates: list[ExtractionCandidate],
    ) -> list[ExtractionCandidate]:
        """Return candidates ranked by deterministic lexical relevance."""

        if not candidates:
            return []

        question_tokens = self._get_question_tokens(
            question
        )

        if not question_tokens:
            return candidates

        scored: list[
            tuple[
                float,
                int,
                ExtractionCandidate,
            ]
        ] = []

        for index, candidate in enumerate(
            candidates
        ):
            score = self._score_candidate(
                question_tokens=question_tokens,
                candidate=candidate,
            )

            scored.append(
                (
                    score,
                    index,
                    candidate,
                )
            )

        scored.sort(
            key=lambda item: (
                -item[0],
                item[1],
            )
        )

        return [
            candidate
            for _, _, candidate in scored
        ]

    def select_for_prompt(
        self,
        question: str,
        candidates: list[ExtractionCandidate],
    ) -> list[ExtractionCandidate]:
        """Return strongly relevant bounded candidates for the LLM."""

        ranked = self.rank(
            question=question,
            candidates=candidates,
        )

        if not ranked:
            return []

        question_tokens = self._get_question_tokens(
            question
        )

        if not question_tokens:
            return ranked[
                :self.maximum_candidates
            ]

        scored = [
            (
                self._score_candidate(
                    question_tokens=question_tokens,
                    candidate=candidate,
                ),
                candidate,
            )
            for candidate in ranked
        ]

        highest_score = scored[0][0]

        if highest_score <= 0.0:
            return ranked[
                :self.maximum_candidates
            ]

        minimum_score = (
            highest_score
            * self.minimum_relative_score
        )

        relevant = [
            candidate
            for score, candidate in scored
            if score >= minimum_score
        ]

        return relevant[
            :self.maximum_candidates
        ]


    def _score_candidate(
        self,
        question_tokens: list[str],
        candidate: ExtractionCandidate,
    ) -> float:
        """Return lexical relevance of one extraction candidate."""

        structural_text = " ".join(
            part
            for part in (
                candidate.heading,
                candidate.structural_context,
            )
            if part
        )

        structural_tokens = self.keyword_tokenizer.tokenize(
            structural_text
        )

        fact_tokens = self.keyword_tokenizer.tokenize(
            candidate.source_quote
        )

        structural_score = self.keyword_scorer.score(
            query_tokens=question_tokens,
            content_tokens=structural_tokens,
        )

        fact_score = self.keyword_scorer.score(
            query_tokens=question_tokens,
            content_tokens=fact_tokens,
        )

        return (
            structural_score * 0.7
            + fact_score * 0.3
        )

    def _candidate_evidence_text(
        self,
        candidate: ExtractionCandidate,
    ) -> str:
        """Return structural and factual evidence used for lexical ranking."""

        return " ".join(
            part
            for part in (
                candidate.heading,
                candidate.structural_context,
                candidate.source_quote,
            )
            if part
        )

    def _get_question_tokens(
        self,
        question: str,
    ) -> list[str]:
        """Return meaningful normalized question tokens."""

        tokens = self.keyword_tokenizer.tokenize(
            question
        )

        return [
            token
            for token in tokens
            if len(token) >= 3
            and token not in self._KEYWORD_STOP_WORDS
        ]
