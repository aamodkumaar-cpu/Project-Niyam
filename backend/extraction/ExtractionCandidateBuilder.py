"""
Extraction Candidate Builder.

Type:
    Domain Service

Purpose:
    Convert retrieved source text into deterministic extraction candidates
    while preserving the structural context surrounding each fact.

Responsibilities:
    - Identify explicit factual list items.
    - Preserve factual wording from the source.
    - Preserve structural context preceding each fact.
    - Associate each fact with its nearest structural heading.
    - Split independently stated sentences into atomic candidates.
    - Produce stable candidate identifiers.

Does NOT:
    - Interpret the business meaning of headings.
    - Decide whether a heading represents a company, person,
      product, section, or any other domain concept.
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

    _OCR_CHARACTER_SEPARATOR_PATTERN = re.compile(
        r"(?<=\S)\s+>\s+(?=\S)"
    )

    _PAGE_NUMBER_PATTERN = re.compile(
        r"^\d+(?:\s+\d+)?\.?$"
    )

    _QUESTION_PATTERN = re.compile(
        r"\?$"
    )

    def build(
        self,
        knowledge_nodes: list[KnowledgeNode],
        relationship: bool = False,
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
                    relationship=relationship,
                )
            )

        return candidates


    def _build_node_candidates(
        self,
        node_index: int,
        node: KnowledgeNode,
        relationship: bool = False,
    ) -> list[ExtractionCandidate]:
        """Build factual candidates from one retrieved node."""

        source = self._normalize_source_layout(
            node.content
        )

        if self._is_question_activity_page(source):
            return []

        matches = list(
            self._BULLET_PATTERN.finditer(
                source
            )
        )

        if not matches:
            return self._build_non_bullet_candidate(
                node_index=node_index,
                node=node,
                source=source,
                relationship=relationship,
            )

        candidates: list[ExtractionCandidate] = []
        structural_context: list[str] = []
        candidate_number = 0

        for match_index, match in enumerate(matches):
            prefix = source[:match.start()]

            headings = self._extract_structural_headings(
                prefix
            )

            if headings:
                structural_context = headings

            start = match.end()

            end = (
                matches[match_index + 1].start()
                if match_index + 1 < len(matches)
                else len(source)
            )

            raw_quote = source[start:end]

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

                    heading = (
                        structural_context[-1]
                        if structural_context
                        else ""
                    )

                    context = self._format_structural_context(
                        structural_context
                    )

                    candidates.append(
                        ExtractionCandidate(
                            candidate_id=(
                                f"C{node_index}_{candidate_number}"
                            ),
                            heading=heading,
                            structural_context=context,
                            source_quote=fragment,
                            node=node,
                        )
                    )

            if trailing_heading:
                structural_context = (
                    self._replace_trailing_heading(
                        structural_context,
                        trailing_heading,
                    )
                )

        return candidates



    def _build_relationship_quote(
        self,
        fragments: list[str],
        fragment_index: int,
    ) -> str:
        """Build source-grounded evidence for a relationship without duplicating candidates."""

        if not fragments:
            return ""

        current = fragments[fragment_index]

        if fragment_index == 0:
            if len(fragments) > 1:
                return f"{current} {fragments[fragment_index + 1]}"

            return current

        if fragment_index == len(fragments) - 1:
            return f"{fragments[fragment_index - 1]} {current}"

        return f"{fragments[fragment_index - 1]} {current}"



    def _build_non_bullet_candidate(
        self,
        node_index: int,
        node: KnowledgeNode,
        source: str,
        relationship: bool = False,
    ) -> list[ExtractionCandidate]:
        """Build candidates from source text without explicit bullets."""

        headings, body = (
            self._extract_structural_context_from_source(
                source
            )
        )

        quote = self._normalize_whitespace(
            body
        )

        if not quote:
            return []

        fragments = self._split_atomic_fragments(
            quote
        )

        if not fragments:
            return []

        heading = (
            headings[-1]
            if headings
            else ""
        )

        context = self._format_structural_context(
            headings
        )

        return [
            ExtractionCandidate(
                candidate_id=f"C{node_index}_{index}",
                heading=heading,
                structural_context=context,
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
        text: str,
    ) -> list[str]:
        """Split text into deterministic atomic candidate fragments."""

        fragments: list[str] = []

        for fragment in re.split(
            r"(?<=[.!?])\s+(?=[A-Z0-9])",
            text,
        ):
            normalized = self._normalize_whitespace(
                fragment
            )

            if not normalized:
                continue

            normalized = self._strip_leading_question_number(
                normalized
            )

            if not self._is_meaningful_candidate(
                normalized
            ):
                continue

            fragments.append(normalized)

        return fragments




    def _is_meaningful_candidate(self, text: str) -> bool:
        """Return whether text is meaningful enough to become a candidate."""

        normalized = text.strip()

        if not normalized:
            return False

        if normalized.rstrip(".").isdigit():
            return False

        # Any question-shaped fragment is non-evidence.
        if "?" in normalized:
            return False

        lower = normalized.lower()

        instruction_prefixes = (
            "explain",
            "discuss",
            "prepare ",
            "develop ",
            "create ",
            "document ",
            "translate ",
            "divide ",
            "observe ",
            "identify ",
            "describe ",
            "compare ",
            "write ",
            "list ",
            "state ",
            "answer ",
            "each group will ",
            "the project should ",
        )

        if lower.startswith(instruction_prefixes):
            return False

        if re.fullmatch(
            r"(?:fig\.?|figure|chapter|page)\s*\d*(?:\.\d+)?",
            lower,
        ):
            return False

        # PDF footer/header contamination.
        if "chapter 2.indd" in lower:
            return False

        if re.search(
            r"\d{1,2}:\d{2}:\d{2}\s*(?:am|pm)",
            lower,
        ):
            return False

        return True



    def _strip_leading_question_number(
        self,
        text: str,
    ) -> str:
        """Remove a numbered question prefix from source text."""

        return re.sub(
            r"^\s*\d+\.\s*",
            "",
            text.strip(),
        )


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

            if self._looks_like_heading(
                suffix
            ):
                return (
                    normalized[
                        :match.start() + 1
                    ].strip(),
                    suffix,
                )

        return normalized, ""

    def _extract_structural_headings(
        self,
        prefix: str,
    ) -> list[str]:
        """Extract structurally separate headings preceding a candidate."""

        if not prefix.strip():
            return []

        lines = self._prepare_lines(
            prefix
        )

        if not lines:
            return []

        headings: list[str] = []

        for line in lines:
            if self._looks_like_heading(line):
                headings.append(line)

        return self._deduplicate_adjacent(
            headings
        )



    def _extract_structural_context_from_source(
        self,
        source: str,
    ) -> tuple[list[str], str]:
        """Separate leading structural headings from source content."""

        lines = self._prepare_lines(
            source
        )

        if not lines:
            return [], ""

        headings: list[str] = []
        body_lines: list[str] = []

        for line in lines:
            if not body_lines and self._looks_like_heading(line):
                headings.append(line)
                continue

            body_lines.append(line)

        if not body_lines:
            return headings, ""

        return headings, " ".join(body_lines)




    def _prepare_lines(
        self,
        text: str,
    ) -> list[str]:
        """Normalize source layout while preserving meaningful line boundaries."""

        raw_lines = text.splitlines()

        lines: list[str] = []
        in_activity_block = False

        for raw_line in raw_lines:
            normalized = self._normalize_layout_text(
                raw_line
            )

            if not normalized:
                continue

            if self._is_non_factual_source_line(
                normalized
            ):
                in_activity_block = True
                continue

            if in_activity_block:
                if self._is_activity_continuation(
                    normalized
                ):
                    continue

                in_activity_block = False

            lines.append(normalized)

        return lines



    def _normalize_source_layout(
        self,
        text: str,
    ) -> str:
        """Normalize common PDF/OCR layout artifacts."""

        if not text:
            return ""

        lines = [
            self._normalize_layout_text(line)
            for line in text.splitlines()
        ]

        lines = [
            line
            for line in lines
            if line
        ]

        return "\n".join(lines)

    def _normalize_layout_text(
        self,
        text: str,
    ) -> str:
        """Normalize OCR character separators and layout whitespace."""

        value = text.strip()

        if not value:
            return ""

        # PDF extraction can represent a heading as:
        #
        # S > h > a > p > i > n > g
        #
        # Convert that representation back into readable text.
        if self._looks_like_character_spaced_text(
            value
        ):
            value = self._collapse_character_spaced_text(
                value
            )

        # Remove common bullet artifacts from structural text.
        value = re.sub(
            r"^[Æ●•▪◦‣]\s*",
            "",
            value,
        )

        # Normalize repeated whitespace.
        value = " ".join(
            value.split()
        ).strip()

        return value

    def _looks_like_character_spaced_text(
        self,
        text: str,
    ) -> bool:
        """Return whether text appears to contain OCR character separators."""

        if ">" not in text:
            return False

        parts = [
            part.strip()
            for part in text.split(">")
        ]

        if len(parts) < 4:
            return False

        meaningful_parts = [
            part
            for part in parts
            if part
        ]

        if not meaningful_parts:
            return False

        single_character_parts = sum(
            1
            for part in meaningful_parts
            if len(part) <= 1
        )

        return (
            single_character_parts
            / len(meaningful_parts)
            >= 0.6
        )


    def _collapse_character_spaced_text(
        self,
        text: str,
    ) -> str:
        """Collapse OCR character-separated text into readable text."""

        parts = text.split(">")

        result: list[str] = []

        for part in parts:
            if not part.strip():
                result.append(" ")
                continue

            result.append(part.strip())

        value = "".join(result)

        value = re.sub(
            r"\s{2,}",
            " ",
            value,
        )

        return value.strip()



    def _replace_trailing_heading(
        self,
        context: list[str],
        heading: str,
    ) -> list[str]:
        """Replace the current leaf heading with a newly discovered heading."""

        normalized_heading = self._normalize_layout_text(
            heading
        )

        if not normalized_heading:
            return context

        if not context:
            return [normalized_heading]

        if context[-1] == normalized_heading:
            return context

        return [
            *context[:-1],
            normalized_heading,
        ]

    def _format_structural_context(
        self,
        headings: list[str],
    ) -> str:
        """Format structural headings as one stable string."""

        cleaned = [
            self._normalize_layout_text(
                heading
            )
            for heading in headings
            if self._normalize_layout_text(
                heading
            )
        ]

        cleaned = self._deduplicate_adjacent(
            cleaned
        )

        return " > ".join(
            cleaned
        )

    def _deduplicate_adjacent(
        self,
        values: list[str],
    ) -> list[str]:
        """Remove immediately repeated structural headings."""

        result: list[str] = []

        for value in values:
            if not result or result[-1] != value:
                result.append(value)

        return result

    def _looks_like_heading(
        self,
        text: str,
    ) -> bool:
        """Return whether text appears structurally separate from prose."""

        value = self._normalize_layout_text(
            text
        )

        if not value:
            return False

        # Page numbers and numbered question markers are not headings.
        if self._PAGE_NUMBER_PATTERN.fullmatch(
            value
        ):
            return False

        # Questions are content, not headings.
        if self._QUESTION_PATTERN.search(
            value
        ):
            return False

        # Very long lines are almost certainly prose.
        if len(value) > 120:
            return False

        words = value.split()

        if not words:
            return False

        # Textbook/page headers containing the book title and grade
        # are structural metadata, not factual evidence.
        if (
            "Understanding Society" in value
            or "Grade 9" in value
            or re.match(r"^\d+\s+2\s+–\s+", value)
        ):
            return True

        if len(words) > 12:
            return False

        # A heading should not look like a sentence fragment.
        if value.endswith(
            (".", "!", "?")
        ):
            return False

        # Common PDF extraction artifacts should never become headings.
        if value.startswith(
            (
                "Chapter ",
                "Fig.",
                "Figure ",
                "LET'S ",
                "LET’S ",
                "DON'T ",
                "DON’T ",
                "Questions ",
            )
        ):
            return False

        # Headings containing explicit structural punctuation
        # are strong candidates.
        if ":" in value:
            return True

        if "|" in value:
            return True

        if "(" in value and ")" in value:
            return True

        # All-uppercase text is normally a section heading.
        if value.isupper() and len(words) <= 10:
            return True

        # Very short fragments are usually OCR artifacts.
        if len(words) == 1:
            return len(value) >= 4

        # A heading normally has title-like capitalization.
        capitalized_words = sum(
            1
            for word in words
            if word
            and word[0].isupper()
        )

        return (
            capitalized_words
            >= max(
                1,
                len(words) // 2,
            )
        )

    def _normalize_whitespace(
        self,
        text: str,
    ) -> str:
        """Normalize layout whitespace without changing factual wording."""

        return " ".join(
            text.split()
        ).strip()




    def _is_non_factual_source_line(
        self,
        text: str,
    ) -> bool:
        """Return whether a source line is clearly non-factual."""

        normalized = text.strip()

        if not normalized:
            return True

        lower = normalized.lower()

        # Standalone page / figure / chapter artifacts.
        if re.fullmatch(
            r"(?:fig\.?|figure|chapter|page)\s*\d*(?:\.\d+)?",
            lower,
        ):
            return True

        # PDF footer artifacts.
        if re.match(
            r"^chapter\s+\d+\.indd",
            lower,
        ):
            return True

        # Numbered textbook questions and activities.
        if re.match(
            r"^\d+\.\s+",
            normalized,
        ):
            return True

        # Continuation lines belonging to textbook instructions.
        instruction_prefixes = (
            "explain",
            "discuss",
            "develop a plan",
            "prepare ",
            "create ",
            "document ",
            "translate ",
            "divide ",
            "which disasters",
            "what precautionary",
            "what ",
            "how ",
        )

        if lower.startswith(instruction_prefixes):
            return True

        return False



    def _is_activity_continuation(
        self,
        text: str,
    ) -> bool:
        """Return whether text continues a numbered textbook activity."""

        normalized = text.strip().lower()

        return normalized.startswith(
            (
                "discuss ",
                "explain ",
                "each group ",
                "the project ",
            )
        )



    def _is_question_activity_page(
        self,
        source: str,
    ) -> bool:
        """Return whether source is primarily a textbook question/activity page."""

        normalized = self._normalize_whitespace(
            source
        )

        if not normalized:
            return True

        # PDF extraction may flatten an entire page/chunk into one line.
        # Therefore activity detection must work independently of line
        # boundaries.
        numbered_items = re.findall(
            r"(?:^|\s)\d+\.\s+",
            normalized,
        )

        if len(numbered_items) < 2:
            return False

        question_count = len(
            re.findall(
                r"\?",
                normalized,
            )
        )

        instruction_count = len(
            re.findall(
                r"\b(?:explain|discuss|develop|prepare|create|"
                r"document|translate|divide|identify|describe|"
                r"compare|write|list|state|answer)\b",
                normalized,
                flags=re.IGNORECASE,
            )
        )

        # A numbered page containing several questions/instructions is
        # an activity page, not factual evidence.
        return (
            question_count > 0
            and instruction_count >= 2
        )


    def _prepare_lines_for_activity_detection(
        self,
        text: str,
    ) -> list[str]:
        """Normalize source lines for activity-page classification."""

        lines: list[str] = []

        for raw_line in text.splitlines():
            normalized = self._normalize_layout_text(
                raw_line
            )

            if normalized:
                lines.append(normalized)

        return lines