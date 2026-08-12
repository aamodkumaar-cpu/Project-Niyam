"""
Extraction Candidate Builder.

Type:
    Domain Service

Purpose:
    Convert retrieved source text into deterministic extraction candidates.

Responsibilities:
    - Identify explicit factual list items.
    - Preserve factual wording from the source.
    - Associate each fact with its nearest structural heading.
    - Split independently stated sentences into atomic candidates.
    - Produce stable candidate identifiers.

Does NOT:
    - Decide which facts answer a question.
    - Call the LLM.
    - Invent or rewrite source text.
"""

from __future__ import annotations

import re

from backend.extraction.ExtractionCandidate import ExtractionCandidate
from backend.retrieval.KnowledgeNode import KnowledgeNode


class ExtractionCandidateBuilder:
    """Build deterministic source candidates for LLM selection."""

    _BULLET_PATTERN = re.compile(
        r"(?:^|\s)(?:●|•|▪|◦|‣|[-*])\s+"
    )

    _SENTENCE_PATTERN = re.compile(
        r"(?<=[.!?])\s+(?=[A-Z0-9])"
    )

    _ROLE_HEADING_PATTERN = re.compile(
        r"(?:^|(?:\n|[ \t]{2,})+)"
        r"([A-Z][^,\n]{0,100},[ \t\n]+"
        r"[^()\n]{1,160}\([^()\n]{1,120}\)"
        r"(?:[ \t]*\|[ \t]*[^●\n]{0,100})?)"
    )

    _SECTION_HEADING_PATTERN = re.compile(
        r"(?:^|(?:\n|[ \t]{2,})+)"
        r"([A-Z][^●\n]{1,180}"
        r"\([^()\n]{1,120}\)"
        r"(?:[ \t]*\|[ \t]*[^●\n]{0,100})?)"
    )

    def build(
        self,
        knowledge_nodes: list[KnowledgeNode],
    ) -> list[ExtractionCandidate]:
        """Build deterministic candidates from retrieved source nodes."""

        candidates: list[ExtractionCandidate] = []

        for node_index, node in enumerate(
            knowledge_nodes,
            start=1,
        ):
            candidates.extend(
                self._build_node_candidates(
                    node_index=node_index,
                    node=node,
                )
            )

        return candidates

    def _build_node_candidates(
        self,
        node_index: int,
        node: KnowledgeNode,
    ) -> list[ExtractionCandidate]:
        """Build factual candidates from one retrieved node."""

        matches = list(
            self._BULLET_PATTERN.finditer(
                node.content
            )
        )

        if not matches:
            return self._build_non_bullet_candidate(
                node_index=node_index,
                node=node,
            )

        candidates: list[ExtractionCandidate] = []
        current_heading = ""
        candidate_number = 0

        for match_index, match in enumerate(matches):
            prefix = node.content[:match.start()]

            explicit_heading = self._extract_heading(
                prefix
            )

            if explicit_heading:
                current_heading = explicit_heading

            start = match.end()

            end = (
                matches[match_index + 1].start()
                if match_index + 1 < len(matches)
                else len(node.content)
            )

            raw_quote = node.content[start:end]

            raw_quote, trailing_heading = (
                self._split_trailing_heading(
                    raw_quote
                )
            )

            quote = self._normalize_whitespace(
                raw_quote
            )

            if quote:
                fragments = self._split_atomic_fragments(
                    quote
                )

                for fragment in fragments:
                    candidate_number += 1

                    candidates.append(
                        ExtractionCandidate(
                            candidate_id=(
                                f"C{node_index}_{candidate_number}"
                            ),
                            heading=current_heading,
                            source_quote=fragment,
                            node=node,
                        )
                    )

            if trailing_heading:
                current_heading = trailing_heading

        return candidates

    def _build_non_bullet_candidate(
        self,
        node_index: int,
        node: KnowledgeNode,
    ) -> list[ExtractionCandidate]:
        """Build candidates from source text without explicit bullets."""

        source = node.content

        heading = self._fallback_heading(
            source
        )

        quote = self._normalize_whitespace(
            source
        )

        if not quote:
            return []

        fragments = self._split_atomic_fragments(
            quote
        )

        return [
            ExtractionCandidate(
                candidate_id=(
                    f"C{node_index}_{index}"
                ),
                heading=heading,
                source_quote=fragment,
                node=node,
            )
            for index, fragment in enumerate(
                fragments,
                start=1,
            )
        ]

    def _split_atomic_fragments(
        self,
        quote: str,
    ) -> list[str]:
        """Split independently stated sentences into atomic candidates."""

        fragments = [
            fragment.strip()
            for fragment in self._SENTENCE_PATTERN.split(
                quote
            )
            if fragment.strip()
        ]

        return fragments or [quote]

    def _split_trailing_heading(
        self,
        text: str,
    ) -> tuple[str, str]:
        """Separate a structural heading attached after a factual fragment."""

        normalized = self._normalize_whitespace(
            text
        )

        if not normalized:
            return "", ""

        matches = list(
            re.finditer(
                r"\.\s+(?=[A-Z])",
                normalized,
            )
        )

        for match in reversed(matches):
            suffix = normalized[
                match.end():
            ].strip()

            if self._looks_like_structural_heading(
                suffix
            ):
                return (
                    normalized[
                        :match.start() + 1
                    ].strip(),
                    suffix,
                )

        return normalized, ""

    def _extract_heading(
        self,
        prefix: str,
    ) -> str:
        """Extract the nearest structural heading before a factual bullet."""

        if not prefix.strip():
            return ""

        # Prefer structure that appears after the last completed factual
        # sentence. This prevents an older company heading from leaking
        # into a later section such as Education & Certifications.
        sentence_boundaries = list(
            re.finditer(
                r"\.\s+(?=[A-Z])",
                prefix,
            )
        )

        last_sentence_end = (
            sentence_boundaries[-1].end() - 1
            if sentence_boundaries
            else -1
        )

        structural_prefix = (
            prefix[
                last_sentence_end + 1:
            ]
            if last_sentence_end >= 0
            else prefix
        )

        role_matches = list(
            self._ROLE_HEADING_PATTERN.finditer(
                structural_prefix
            )
        )

        section_matches = list(
            self._SECTION_HEADING_PATTERN.finditer(
                structural_prefix
            )
        )

        matches = role_matches + section_matches

        if matches:
            match = max(
                matches,
                key=lambda item: item.start(),
            )

            return self._normalize_whitespace(
                match.group(1)
            )

        suffix = self._normalize_whitespace(
            structural_prefix
        )

        if self._looks_like_structural_heading(
            suffix
        ):
            return suffix

        lines = [
            self._normalize_whitespace(line)
            for line in structural_prefix.splitlines()
            if self._normalize_whitespace(line)
        ]

        if lines:
            candidate = lines[-1]

            if self._looks_like_structural_heading(
                candidate
            ):
                return candidate

        return ""

    def _fallback_heading(
        self,
        source: str,
    ) -> str:
        """Return an explicitly represented structural heading."""

        lines = [
            self._normalize_whitespace(line)
            for line in source.splitlines()
            if self._normalize_whitespace(line)
        ]

        if (
            len(lines) >= 2
            and self._looks_like_structural_heading(
                lines[0]
            )
        ):
            return lines[0]

        return ""

    def _looks_like_structural_heading(
        self,
        text: str,
    ) -> bool:
        """Return whether text has structural-heading characteristics."""

        value = self._normalize_whitespace(
            text
        )

        if not value:
            return False

        if len(value) > 180:
            return False

        if value.endswith(
            (".", "!", "?")
        ):
            return False

        if self._ROLE_HEADING_PATTERN.fullmatch(
            value
        ):
            return True

        if self._SECTION_HEADING_PATTERN.fullmatch(
            value
        ):
            return True

        if " | " in value:
            return True

        if "(" in value and ")" in value:
            return True

        # Generic short headings such as "Company A".
        if (
            len(value.split()) <= 12
            and not self._looks_like_sentence(
                value
            )
        ):
            return True

        return False

    def _looks_like_sentence(
        self,
        text: str,
    ) -> bool:
        """Return whether text has sentence-like characteristics."""

        value = text.strip()

        if value.endswith(
            (".", "!", "?")
        ):
            return True

        return False

    def _normalize_whitespace(
        self,
        text: str,
    ) -> str:
        """Normalize layout whitespace without changing factual wording."""

        return " ".join(
            text.split()
        ).strip()