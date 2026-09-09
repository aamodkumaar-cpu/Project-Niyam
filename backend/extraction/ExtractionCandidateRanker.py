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
    - Preserve structural coverage when structural evidence is required.

Does NOT:

    - Retrieve knowledge.
    - Interpret facts.
    - Validate source evidence.
    - Call the LLM.
    - Generate answers.
    - Apply domain-specific entity rules.
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
        self.minimum_relative_score = minimum_relative_score

    def rank(
        self,
        question: str,
        candidates: list[ExtractionCandidate],
        evidence_requirement: EvidenceRequirement | None = None,
    ) -> list[ExtractionCandidate]:
        """Return candidates ranked by deterministic evidence relevance."""

        if not candidates:
            return []

        question_tokens = self._get_question_tokens(question)

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
        """Return a bounded evidence set for the LLM."""

        ranked = self.rank(
            question=question,
            candidates=candidates,
            evidence_requirement=evidence_requirement,
        )

        if not ranked:
            return []

        question_tokens = self._get_question_tokens(question)

        if not question_tokens:
            return ranked[: self.maximum_candidates]

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
            if requirement.structural_value_required:
                return self._select_structural_candidates(
                    ranked=ranked,
                    maximum_candidates=self.maximum_candidates,
                )

            return ranked[: self.maximum_candidates]

        minimum_score = (
            highest_score * self.minimum_relative_score
        )

        relevant = [
            candidate
            for score, candidate in scored
            if score >= minimum_score
        ]

        if not requirement.structural_value_required:
            return relevant[: self.maximum_candidates]

        return self._select_with_structural_coverage(
            ranked=ranked,
            relevant=relevant,
            maximum_candidates=self.maximum_candidates,
        )

    def _select_with_structural_coverage(
        self,
        ranked: list[ExtractionCandidate],
        relevant: list[ExtractionCandidate],
        maximum_candidates: int,
    ) -> list[ExtractionCandidate]:
        """Preserve structural coverage while respecting the candidate bound."""

        selected: list[ExtractionCandidate] = []
        selected_ids: set[str] = set()
        represented_groups: set[str] = set()

        structural_candidates = [
            candidate
            for candidate in ranked
            if self._has_structural_evidence(candidate)
        ]

        for candidate in structural_candidates:
            group_key = self._get_structural_group_key(candidate)

            if group_key in represented_groups:
                continue

            selected.append(candidate)
            selected_ids.add(candidate.candidate_id)
            represented_groups.add(group_key)

            if len(selected) >= maximum_candidates:
                return selected

        for candidate in relevant:
            if candidate.candidate_id in selected_ids:
                continue

            selected.append(candidate)
            selected_ids.add(candidate.candidate_id)

            if len(selected) >= maximum_candidates:
                return selected

        for candidate in ranked:
            if candidate.candidate_id in selected_ids:
                continue

            selected.append(candidate)
            selected_ids.add(candidate.candidate_id)

            if len(selected) >= maximum_candidates:
                break

        return selected

    def _select_structural_candidates(
        self,
        ranked: list[ExtractionCandidate],
        maximum_candidates: int,
    ) -> list[ExtractionCandidate]:
        """Select bounded candidates while preserving structural coverage."""

        selected: list[ExtractionCandidate] = []
        represented_groups: set[str] = set()

        for candidate in ranked:
            if not self._has_structural_evidence(candidate):
                continue

            group_key = self._get_structural_group_key(candidate)

            if group_key in represented_groups:
                continue

            selected.append(candidate)
            represented_groups.add(group_key)

            if len(selected) >= maximum_candidates:
                break

        if len(selected) >= maximum_candidates:
            return selected

        selected_ids = {
            candidate.candidate_id
            for candidate in selected
        }

        for candidate in ranked:
            if candidate.candidate_id in selected_ids:
                continue

            selected.append(candidate)

            if len(selected) >= maximum_candidates:
                break

        return selected

    def _has_structural_evidence(
        self,
        candidate: ExtractionCandidate,
    ) -> bool:
        """Return whether the candidate contains structural evidence."""

        return bool(
            self._normalize_structural_text(
                candidate.heading
            )
            or self._normalize_structural_text(
                candidate.structural_context
            )
        )

    def _get_structural_group_key(
        self,
        candidate: ExtractionCandidate,
    ) -> str:
        """Return a deterministic key representing one structural context."""

        heading = self._normalize_structural_text(
            candidate.heading
        )

        if heading:
            return f"heading:{heading}"

        structural_context = self._normalize_structural_text(
            candidate.structural_context
        )

        if structural_context:
            return f"context:{structural_context}"

        return f"candidate:{candidate.candidate_id}"

    def _normalize_structural_text(
        self,
        text: str,
    ) -> str:
        """Normalize structural text for deterministic grouping."""

        return " ".join(
            text.split()
        ).casefold()

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