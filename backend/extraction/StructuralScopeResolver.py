"""
Structural Scope Resolver.

Type:
    Domain Service

Purpose:
    Resolve the structural scope of candidates for exhaustive extraction.

Responsibilities:
    - Identify structural peers from selected candidates.
    - Preserve candidates that share the same structural evidence pattern.
    - Use generic evidence characteristics rather than domain vocabulary.
    - Prevent unrelated structural sections from entering exhaustive extraction.

Does NOT:
    - Know business domains.
    - Know company names.
    - Know resume or employment concepts.
    - Perform semantic retrieval.
    - Select final facts.
    - Rewrite source content.
"""

from __future__ import annotations

from backend.extraction.EvidenceSignalDetector import (
    EvidenceSignalDetector,
)
from backend.extraction.ExtractionCandidate import (
    ExtractionCandidate,
)


class StructuralScopeResolver:
    """Resolve generic structural scope for exhaustive extraction."""

    def __init__(
        self,
        evidence_signal_detector: EvidenceSignalDetector,
    ) -> None:
        """Initialize the structural scope resolver."""

        self.evidence_signal_detector = (
            evidence_signal_detector
        )

    def resolve(
        self,
        selected_candidates: list[ExtractionCandidate],
        candidates: list[ExtractionCandidate],
    ) -> list[ExtractionCandidate]:
        """Return candidates belonging to the structural scope of selected evidence."""

        if not selected_candidates:
            return []

        if not candidates:
            return []

        selected_signatures = {
            self._structural_signature(candidate)
            for candidate in selected_candidates
            if self._has_structural_value(candidate)
        }

        if not selected_signatures:
            return selected_candidates

        resolved: list[ExtractionCandidate] = []

        for candidate in candidates:
            if (
                self._structural_signature(candidate)
                in selected_signatures
            ):
                resolved.append(candidate)

        return resolved

    def _structural_signature(
        self,
        candidate: ExtractionCandidate,
    ) -> tuple[bool, bool, bool]:
        """Build a generic structural signature for a candidate."""

        heading = candidate.heading or ""
        context = candidate.structural_context or ""

        return (
            self.evidence_signal_detector.has_temporal_value(
                heading
            ),
            self.evidence_signal_detector.has_temporal_value(
                context
            ),
            bool(context.strip()),
        )

    def _has_structural_value(
        self,
        candidate: ExtractionCandidate,
    ) -> bool:
        """Return whether a candidate contains structural evidence."""

        return bool(
            candidate.heading.strip()
            or candidate.structural_context.strip()
        )