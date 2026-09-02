"""
Type:
    Domain Service

Purpose:
    Rank extraction candidates using deterministic lexical relevance
    and generic evidence characteristics.

Responsibilities:
    - Calculate candidate-level lexical relevance.
    - Use structural scope to establish question relevance.
    - Evaluate generic evidence characteristics through EvidenceSignalDetector.
    - Rank candidates deterministically.
    - Select a bounded evidence set for LLM processing.

Does NOT:
    - Retrieve knowledge.
    - Interpret facts.
    - Validate source evidence.
    - Call the LLM.
    - Generate answers.
"""

from __future__ import annotations

from backend.extraction.EvidenceRequirement import (
    EvidenceRequirement,
)
from backend.extraction.EvidenceSignalDetector import (
    EvidenceSignalDetector,
)
from backend.extraction.ExtractionCandidate import (
    ExtractionCandidate,
)
from backend.retrieval.KeywordScorer import KeywordScorer
from backend.retrieval.KeywordTokenizer import KeywordTokenizer


class ExtractionCandidateRanker:
    """Rank extraction candidates using deterministic evidence relevance."""

    _KEYWORD_STOP_WORDS: frozenset[str] = frozenset(
        {
            "the",
            "a",
            "an",
            "and",
            "or",
            "is",
            "are",
            "was",
            "were",
            "what",
            "which",
            "who",
            "where",
            "when",
            "how",
            "why",
            "did",
            "does",
            "do",
            "has",
            "have",
            "had",
            "with",
            "for",
            "from",
            "about",
            "tell",
            "me",
            "all",
            "any",
            "each",
            "every",
            "other",
            "their",
            "its",
            "his",
            "her",
            "this",
            "that",
            "these",
            "those",
            "can",
            "could",
            "would",
            "should",
            "be",
            "been",
            "being",
            "to",
            "of",
            "in",
            "on",
            "at",
            "by",
            "as",
            "into",
            "during",
            "through",
            "than",
            "also",
            "related",
            "associated",
        }
    )

    def __init__(
        self,
        keyword_tokenizer: KeywordTokenizer,
        keyword_scorer: KeywordScorer,
        evidence_signal_detector: EvidenceSignalDetector,
        maximum_candidates: int = 20,
        minimum_relative_score: float = 0.50,
    ) -> None:
        """Initialize the candidate ranker."""

        self.keyword_tokenizer = keyword_tokenizer
        self.keyword_scorer = keyword_scorer
        self.evidence_signal_detector = evidence_signal_detector
        self.maximum_candidates = maximum_candidates
        self.minimum_relative_score = (
            minimum_relative_score
        )

    def rank(
        self,
        question: str,
        candidates: list[ExtractionCandidate],
        evidence_requirement: EvidenceRequirement | None = None,
    ) -> list[ExtractionCandidate]:
        """Return candidates ranked by deterministic evidence relevance."""

        if not candidates:
            return []

        question_tokens = self._get_question_tokens(
            question
        )

        if not question_tokens:
            return candidates

        requirement = (
            evidence_requirement
            if evidence_requirement is not None
            else EvidenceRequirement()
        )

        scored: list[
            tuple[
                float,
                int,
                ExtractionCandidate,
            ]
        ] = []

        for index, candidate in enumerate(candidates):
            score = self._score_candidate(
                question_tokens=question_tokens,
                candidate=candidate,
                evidence_requirement=requirement,
            )

            scored.append(
                (
                    score,
                    -index,
                    candidate,
                )
            )

        scored.sort(
            key=lambda item: (
                item[0],
                item[1],
            ),
            reverse=True,
        )

        return [
            candidate
            for _, _, candidate in scored
        ]

    def select_for_prompt(
        self,
        question: str,
        candidates: list[ExtractionCandidate],
        evidence_requirement: EvidenceRequirement | None = None,
    ) -> list[ExtractionCandidate]:
        """Return a bounded set of highest-ranked candidates for the LLM."""

        ranked = self.rank(
            question=question,
            candidates=candidates,
            evidence_requirement=evidence_requirement,
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

        requirement = (
            evidence_requirement
            if evidence_requirement is not None
            else EvidenceRequirement()
        )

        scored = [
            (
                self._score_candidate(
                    question_tokens=question_tokens,
                    candidate=candidate,
                    evidence_requirement=requirement,
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
        evidence_requirement: EvidenceRequirement | None = None,
    ) -> float:
        """Return deterministic relevance of one extraction candidate."""

        structural_text = " ".join(
            part
            for part in (
                candidate.heading,
                candidate.structural_context,
            )
            if part
        )

        structural_tokens = (
            self.keyword_tokenizer.tokenize(
                structural_text
            )
        )

        fact_tokens = (
            self.keyword_tokenizer.tokenize(
                candidate.source_quote
            )
        )

        structural_score = self.keyword_scorer.score(
            query_tokens=question_tokens,
            content_tokens=structural_tokens,
        )

        fact_score = self.keyword_scorer.score(
            query_tokens=question_tokens,
            content_tokens=fact_tokens,
        )

        score = (
            structural_score * 0.7
            + fact_score * 0.3
        )

        if evidence_requirement is None:
            return score

        evidence_text = self._candidate_evidence_text(
            candidate
        )

        if (
            evidence_requirement.quantity_required
            and self.evidence_signal_detector.has_quantity(
                evidence_text
            )
        ):
            score += 0.15

        if (
            evidence_requirement.temporal_value_required
            and self.evidence_signal_detector.has_temporal_value(
                evidence_text
            )
        ):
            score += 0.15

        if (
            evidence_requirement.relationship_required
            and self.evidence_signal_detector.has_relationship(
                evidence_text
            )
        ):
            score += 0.15

        return score

    def _candidate_evidence_text(
        self,
        candidate: ExtractionCandidate,
    ) -> str:
        """Return structural and factual evidence used for signal detection."""

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
        """Return meaningful tokens from the extraction question."""

        tokens = self.keyword_tokenizer.tokenize(
            question
        )

        return [
            token
            for token in tokens
            if len(token) >= 3
            and token not in self._KEYWORD_STOP_WORDS
        ]