from backend.extraction.ExtractionCandidate import ExtractionCandidate
from backend.extraction.EvidenceSignalDetector import EvidenceSignalDetector
from backend.extraction.StructuralScopeResolver import StructuralScopeResolver


class TestStructuralScopeResolver:
    """Tests generic structural scope resolution."""

    def setup_method(self) -> None:
        self.resolver = StructuralScopeResolver(
            evidence_signal_detector=EvidenceSignalDetector()
        )

    def _candidate(
        self,
        candidate_id: str,
        heading: str,
        structural_context: str = "",
    ) -> ExtractionCandidate:
        """Create a candidate for structural scope testing."""

        return ExtractionCandidate(
            candidate_id=candidate_id,
            heading=heading,
            structural_context=structural_context,
            source_quote=heading,
            node=None,  # type: ignore[arg-type]
        )

    def test_resolves_candidates_with_same_structural_signature(self) -> None:
        """Candidates sharing the selected structural signature are retained."""

        selected = [
            self._candidate(
                "cloudera",
                "Senior Engineering Manager, Cloudera (Oct 2022-Jun 2025)",
            )
        ]

        candidates = [
            selected[0],
            self._candidate(
                "oracle",
                "Software Development Manager, Oracle (Nov 2006-May 2019)",
            ),
            self._candidate(
                "education",
                "Education & Certifications",
            ),
        ]

        result = self.resolver.resolve(selected, candidates)

        assert [candidate.candidate_id for candidate in result] == [
            "cloudera",
            "oracle",
        ]

    def test_excludes_structurally_different_candidates(self) -> None:
        """Candidates from a different structural pattern are excluded."""

        selected = [
            self._candidate(
                "experience",
                "Engineering Manager (Mar 2021-Sep 2022)",
            )
        ]

        candidates = [
            selected[0],
            self._candidate(
                "education",
                "Master of Computer Applications",
            ),
            self._candidate(
                "certification",
                "AWS Certified Solutions Architect Associate",
            ),
        ]

        result = self.resolver.resolve(selected, candidates)

        assert [candidate.candidate_id for candidate in result] == [
            "experience",
        ]

    def test_returns_empty_when_nothing_is_selected(self) -> None:
        """No selected evidence produces no structural scope."""

        candidates = [
            self._candidate(
                "candidate-1",
                "Engineering Manager (2021-2022)",
            )
        ]

        result = self.resolver.resolve([], candidates)

        assert result == []

    def test_returns_empty_when_no_candidates_exist(self) -> None:
        """No candidates produce no structural scope."""

        selected = [
            self._candidate(
                "candidate-1",
                "Engineering Manager (2021-2022)",
            )
        ]

        result = self.resolver.resolve(selected, [])

        assert result == []

    def test_preserves_selected_candidates_without_structural_signature(self) -> None:
        """Candidates without structural evidence are preserved."""

        selected = [
            self._candidate(
                "candidate-1",
                "",
                "",
            )
        ]

        result = self.resolver.resolve(
            selected,
            [
                selected[0],
            ],
        )

        assert result == selected

    def test_is_domain_independent(self) -> None:
        """The resolver works with unrelated domain terminology."""

        selected = [
            self._candidate(
                "project-a",
                "Project Alpha (Jan 2024-Dec 2024)",
            )
        ]

        candidates = [
            selected[0],
            self._candidate(
                "project-b",
                "Project Beta (Jan 2023-Dec 2023)",
            ),
            self._candidate(
                "policy",
                "Security Policy",
            ),
        ]

        result = self.resolver.resolve(selected, candidates)

        assert [candidate.candidate_id for candidate in result] == [
            "project-a",
            "project-b",
        ]