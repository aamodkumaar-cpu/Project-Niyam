"""
Extraction Candidate Builder.

Type:

    Domain Service

Purpose:

    Build deterministic, source-grounded extraction candidates from
    retrieved knowledge nodes.

Responsibilities:

    - Normalize common PDF/OCR layout artifacts.
    - Remove clearly non-factual source fragments.
    - Preserve factual source wording.
    - Split source content into atomic evidence candidates.
    - Preserve reliable structural context when available.
    - Produce stable candidate identifiers.

Does NOT:

    - Determine question relevance.
    - Rank candidates.
    - Ask the LLM to select candidates.
    - Invent or rewrite factual content.
"""

from __future__ import annotations

import re

from backend.extraction.ExtractionCandidate import (
    ExtractionCandidate,
)
from backend.retrieval.KnowledgeNode import KnowledgeNode


class ExtractionCandidateBuilder:
    """Build deterministic source candidates for LLM selection."""

    _BULLET_PATTERN = re.compile(
        r"(?:^|\s)(?:●|•|▪|◦|‣|[-*])\s+"
    )

    _SENTENCE_PATTERN = re.compile(
        r"(?<=[.!?])\s+(?=[A-Z0-9])"
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

        if not source:
            return []

        if self._is_question_activity_page(
            source
        ):
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

        for match_index, match in enumerate(
            matches
        ):
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

            raw_quote = source[
                start:end
            ]

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
                    if not self._is_meaningful_candidate(
                        fragment
                    ):
                        continue

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

        candidates: list[ExtractionCandidate] = []

        for index, fragment in enumerate(
            fragments,
            start=1,
        ):
            if not self._is_meaningful_candidate(
                fragment
            ):
                continue

            candidates.append(
                ExtractionCandidate(
                    candidate_id=f"C{node_index}_{index}",
                    heading=heading,
                    structural_context=context,
                    source_quote=fragment,
                    node=node,
                )
            )

        return candidates



    def _split_atomic_fragments(
        self,
        text: str,
    ) -> list[str]:
        """Split cleaned source text into deterministic factual fragments."""

        normalized_text = self._normalize_source_layout(
            text
        )

        if not normalized_text:
            return []

        normalized_text = (
            self._remove_embedded_pdf_artifacts(
                normalized_text
            )
        )

        normalized_text = self._normalize_whitespace(
            normalized_text
        )

        if not normalized_text:
            return []

        # Protect common abbreviation punctuation from being
        # interpreted as sentence boundaries.
        protected = re.sub(
            r"\b(?:Mr|Mrs|Ms|Dr|Prof|Sr|Jr|Rs)\.",
            lambda match: match.group(0).replace(".", "<DOT>"),
            normalized_text,
            flags=re.IGNORECASE,
        )

        fragments: list[str] = []

        for fragment in self._SENTENCE_PATTERN.split(
            protected
        ):
            normalized = fragment.replace(
                "<DOT>",
                ".",
            )

            normalized = self._normalize_whitespace(
                normalized
            )

            if not normalized:
                continue

            normalized = (
                self._strip_leading_question_number(
                    normalized
                )
            )

            if not normalized:
                continue

            if not self._is_meaningful_candidate(
                normalized
            ):
                continue

            fragments.append(
                normalized
            )

        return fragments




    def _is_meaningful_candidate(
        self,
        text: str,
    ) -> bool:
        """Return whether text is meaningful enough to become evidence."""

        normalized = text.strip()

        if not normalized:
            return False

        if normalized.rstrip(".").isdigit():
            return False

        if "?" in normalized:
            return False

        lower = normalized.lower()

        if self._is_diagram_artifact(
            normalized
        ):
            return False

        if self._is_figure_reference(
            normalized
        ):
            return False

        if self._is_instruction_fragment(
            lower
        ):
            return False

        if self._is_pdf_artifact(
            lower
        ):
            return False

        if self._is_label_sequence(
            normalized
        ):
            return False

        return True



    def _find_embedded_label_sequence(
        self,
        words: list[str],
    ) -> int | None:
        """Return the start of an obvious embedded diagram-label sequence."""

        if len(words) < 8:
            return None

        for index in range(1, len(words)):
            suffix = words[index:]

            if len(suffix) < 3:
                continue

            suffix_text = " ".join(
                suffix
            )

            if self._is_diagram_artifact(
                suffix_text
            ):
                return index

        return None




    def _find_embedded_diagram_boundary(
        self,
        text: str,
    ) -> int | None:
        """Find an embedded transition from prose into extracted non-prose content."""

        normalized = self._normalize_whitespace(
            text
        )

        if not normalized:
            return None

        words = normalized.split()

        if len(words) < 12:
            return None

        for index in range(
            6,
            len(words) - 2,
        ):
            prefix = " ".join(
                words[:index]
            )

            suffix = " ".join(
                words[index:]
            )

            if len(prefix.split()) < 8:
                continue

            suffix_words = suffix.split()

            if len(suffix_words) < 3:
                continue

            # A lowercase suffix is normally a continuation of
            # the preceding prose rather than a new non-prose block.
            if suffix_words[0][0].islower():
                continue

            if not (
                self._is_figure_reference(
                    suffix
                )
                or re.search(
                    r"\bfig(?:ure)?\.?\s*\d+(?:\.\d+)*\b",
                    suffix,
                    flags=re.IGNORECASE,
                )
            ):
                continue

            before_figure = re.split(
                r"\bfig(?:ure)?\.?\s*\d+(?:\.\d+)*\b",
                suffix,
                maxsplit=1,
                flags=re.IGNORECASE,
            )[0].strip()

            if not before_figure:
                continue

            fragments = [
                fragment.strip()
                for fragment in re.split(
                    r"\s{2,}|[,;]",
                    before_figure,
                )
                if fragment.strip()
            ]

            if len(fragments) < 2:
                continue

            short_fragments = sum(
                len(fragment.split()) <= 6
                and not fragment.endswith(
                    (".", "!", "?")
                )
                for fragment in fragments
            )

            if short_fragments < 2:
                continue

            previous = words[index - 1]

            if previous.endswith(
                (
                    ",",
                    ";",
                    ":",
                    "-",
                    "—",
                )
            ):
                continue


            return len(
                prefix
            )

        return None




    def _remove_embedded_pdf_artifacts(
        self,
        text: str,
    ) -> str:
        """Remove generic PDF extraction artifacts while preserving factual text."""

        if not text:
            return ""

        raw_lines = text.splitlines()

        lines: list[str] = []

        for raw_line in raw_lines:
            normalized = self._normalize_layout_text(
                raw_line
            )

            if normalized:
                lines.append(
                    normalized
                )

        if not lines:
            return ""

        cleaned_lines: list[str] = []

        # ---------------------------------------------------------
        # First handle embedded transitions inside a line.
        # ---------------------------------------------------------

        normalized_text = self._normalize_whitespace(
            " ".join(lines)
        )

        diagram_boundary = (
            self._find_embedded_diagram_boundary(
                normalized_text
            )
        )

        if diagram_boundary is not None:
            normalized_text = normalized_text[
                :diagram_boundary
            ].strip()

            lines = (
                [normalized_text]
                if normalized_text
                else []
            )

        # ---------------------------------------------------------
        # Then handle explicit PDF artifacts.
        # ---------------------------------------------------------

        for line in lines:

            # Generic InDesign / PDF extraction marker.
            chapter_marker = re.search(
                r"\bchapter\s+\d+\.indd\b",
                line,
                flags=re.IGNORECASE,
            )

            if chapter_marker:
                prefix = line[
                    :chapter_marker.start()
                ].strip()

                if prefix:
                    cleaned_lines.append(
                        prefix
                    )

                break

            # Generic figure / caption reference.
            figure_marker = re.search(
                r"\bfig(?:ure)?\.?\s*\d+(?:\.\d+)*\b",
                line,
                flags=re.IGNORECASE,
            )

            if figure_marker:
                prefix = line[
                    :figure_marker.start()
                ].strip()

                if prefix:
                    cleaned_lines.append(
                        prefix
                    )

                break

            cleaned_lines.append(
                line
            )

        return self._normalize_whitespace(
            " ".join(
                cleaned_lines
            )
        )


    def _find_embedded_non_prose_boundary(
        self,
        lines: list[str],
    ) -> tuple[int, int] | None:
        """Find a conservative line and character boundary before non-prose content."""

        if not lines:
            return None

        line_count = len(lines)

        for index in range(
            line_count
        ):
            current = lines[index]

            # ---------------------------------------------------------
            # Embedded transition inside the current line.
            # ---------------------------------------------------------

            embedded_boundary = (
                self._find_embedded_diagram_boundary(
                    current
                )
            )

            if embedded_boundary is not None:
                return (
                    index,
                    embedded_boundary,
                )

            # ---------------------------------------------------------
            # Complete-line PDF artifacts.
            # ---------------------------------------------------------

            if self._is_pdf_artifact(
                current.lower()
            ):
                return (
                    index,
                    0,
                )

            if self._is_figure_reference(
                current
            ):
                return (
                    index,
                    0,
                )

            # ---------------------------------------------------------
            # Detect a block of short non-prose fragments.
            # ---------------------------------------------------------

            if not self._looks_like_non_prose_fragment(
                current
            ):
                continue

            block_end = index

            while block_end < line_count:
                line = lines[block_end]

                if self._is_pdf_artifact(
                    line.lower()
                ):
                    break

                if self._is_figure_reference(
                    line
                ):
                    break

                if not self._looks_like_non_prose_fragment(
                    line
                ):
                    break

                block_end += 1

            block_length = (
                block_end - index
            )

            if block_length < 3:
                continue

            if block_length >= 4:
                return (
                    index,
                    0,
                )

            if block_end < line_count:
                following = lines[
                    block_end
                ]

                if (
                    self._is_pdf_artifact(
                        following.lower()
                    )
                    or self._is_figure_reference(
                        following
                    )
                ):
                    return (
                        index,
                        0,
                    )

        return None



    def _looks_like_non_prose_fragment(
        self,
        text: str,
    ) -> bool:
        """Return whether a line is a short fragment suitable for block analysis."""

        normalized = self._normalize_whitespace(
            text
        )

        if not normalized:
            return False

        if self._is_pdf_artifact(
            normalized.lower()
        ):
            return False

        if self._is_figure_reference(
            normalized
        ):
            return False

        if normalized.endswith(
            (".", "!", "?")
        ):
            return False

        words = normalized.split()

        # A single word or very short fragment can be part of a
        # diagram, table, label, or other extracted visual content.
        return len(words) <= 6


    def _looks_like_prose_continuation(
        self,
        previous: str,
        current: str,
    ) -> bool:
        """Return whether the current line plausibly continues ordinary prose."""

        previous_normalized = (
            self._normalize_whitespace(
                previous
            )
        )

        current_normalized = (
            self._normalize_whitespace(
                current
            )
        )

        if not previous_normalized:
            return False

        if not current_normalized:
            return False

        # Strong grammatical continuation signals.
        if previous_normalized.endswith(
            (
                ",",
                ";",
                ":",
                "-",
                "—",
            )
        ):
            return True

        current_lower = (
            current_normalized.lower()
        )

        continuation_prefixes = (
            "and ",
            "or ",
            "but ",
            "because ",
            "which ",
            "that ",
            "where ",
            "when ",
            "while ",
            "with ",
            "from ",
            "to ",
            "of ",
            "in ",
            "on ",
            "for ",
            "as ",
            "by ",
        )

        if current_lower.startswith(
            continuation_prefixes
        ):
            return True

        return False



    def _is_dangling_prose_suffix(
        self,
        text: str,
    ) -> bool:
        """Return whether text ends with a likely incomplete grammatical phrase."""

        normalized = self._normalize_whitespace(
            text
        )

        if not normalized:
            return False

        words = normalized.split()

        if len(words) < 2:
            return False

        dangling_words = {
            "a",
            "an",
            "the",
            "this",
            "that",
            "these",
            "those",
            "each",
            "every",
            "some",
            "any",
            "another",
            "other",
            "such",
            "its",
            "their",
            "his",
            "her",
            "our",
            "your",
        }

        return words[-1].lower() in dangling_words



    def _is_embedded_diagram_line(
        self,
        text: str,
    ) -> bool:
        """Return whether a line appears to be a diagram label rather than prose."""

        normalized = self._normalize_whitespace(
            text
        )

        if not normalized:
            return False

        words = normalized.split()

        if len(words) > 10:
            return False

        # Diagram labels frequently contain short noun phrases
        # rather than complete sentences.
        if normalized.endswith(
            (".", "!", "?")
        ):
            return False

        lower = normalized.lower()

        # Strong structural indicators of diagram labels.
        if ":" in normalized:
            return False

        # Short fragments with multiple comma-separated labels
        # are commonly extracted from diagrams.
        comma_parts = [
            part.strip()
            for part in normalized.split(",")
            if part.strip()
        ]

        if (
            len(comma_parts) >= 3
            and len(words) <= 12
        ):
            return True

        # Very short noun-phrase lines are possible diagram labels.
        if (
            2 <= len(words) <= 5
            and not lower.startswith(
                (
                    "the ",
                    "this ",
                    "these ",
                    "there ",
                    "it ",
                    "they ",
                )
            )
        ):
            return True

        return False



    def _is_diagram_artifact(
        self,
        text: str,
    ) -> bool:
        """Return whether text appears to be extracted diagram labels."""

        normalized = " ".join(
            text.split()
        )

        if not normalized:
            return True

        # Typical diagram extraction such as:
        #
        # 1 2 3 4 5 Headland1 Sea arch2 ...
        #
        digit_count = sum(
            character.isdigit()
            for character in normalized
        )

        if digit_count >= 3:
            words = normalized.split()

            if len(words) <= 25:
                return True

        return False

    def _is_figure_reference(
        self,
        text: str,
    ) -> bool:
        """Return whether text is primarily a figure or diagram reference."""

        normalized = text.strip().lower()

        if re.fullmatch(
            r"(?:fig\.?|figure)\s*[a-z0-9.\-]*",
            normalized,
        ):
            return True

        if re.fullmatch(
            r"(?:fig\.?|figure)\s*"
            r"(?:[a-z0-9]+\s*){1,8}",
            normalized,
        ):
            return True

        if normalized.endswith(
            (
                " fig.",
                " fig",
                " figure",
            )
        ):
            words = normalized.split()

            if len(words) <= 8:
                return True

        return False

    def _is_instruction_fragment(
        self,
        lower: str,
    ) -> bool:
        """Return whether text is a textbook instruction rather than evidence."""

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
            "which disasters ",
            "what precautionary ",
        )

        return lower.startswith(
            instruction_prefixes
        )

    def _is_pdf_artifact(
        self,
        lower: str,
    ) -> bool:
        """Return whether text contains obvious PDF extraction artifacts."""

        if "chapter 2.indd" in lower:
            return True

        if re.search(
            r"\d{1,2}:\d{2}:\d{2}\s*(?:am|pm)",
            lower,
        ):
            return True

        if re.fullmatch(
            r"(?:fig\.?|figure|chapter|page)\s*\d*(?:\.\d+)?",
            lower,
        ):
            return True

        return False

    def _is_label_sequence(
        self,
        text: str,
    ) -> bool:
        """Return whether text is primarily a sequence of diagram labels."""

        words = text.split()

        if len(words) < 2:
            return False

        short_numeric_labels = 0

        for word in words:
            cleaned = word.strip(
                ".,:;()-"
            )

            if cleaned.isdigit():
                short_numeric_labels += 1

        return (
            short_numeric_labels >= 2
            and short_numeric_labels
            / len(words)
            >= 0.25
        )

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
        """Separate a reliable structural heading from factual content."""

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



    def _split_structural_bullet_prefix(
        self,
        text: str,
    ) -> tuple[str, str]:
        """Separate text preceding an embedded bullet from the remaining text."""

        normalized = self._normalize_whitespace(
            text
        )

        if not normalized:
            return "", ""

        match = re.search(
            r"\s(?:●|•|▪|◦|‣|[-*])\s+",
            normalized,
        )

        if not match:
            return normalized, ""

        return (
            normalized[:match.start()].strip(),
            normalized[match.end():].strip(),
        )


    def _split_prefix_at_last_bullet(
        self,
        text: str,
    ) -> tuple[str, str]:
        """Separate structural text from content at the last embedded bullet."""

        normalized = self._normalize_whitespace(
            text
        )

        if not normalized:
            return "", ""

        matches = list(
            self._BULLET_PATTERN.finditer(
                normalized
            )
        )

        if not matches:
            return normalized, ""

        match = matches[-1]

        return (
            normalized[:match.start()].strip(),
            normalized[match.end():].strip(),
        )


    def _split_structural_segments(
        self,
        text: str,
    ) -> list[str]:
        """Split source text into structural segments around embedded bullets."""

        normalized = self._normalize_whitespace(
            text
        )

        if not normalized:
            return []

        segments = re.split(
            r"\s+(?=●|•|▪|◦|‣|[-*])\s*",
            normalized,
        )

        return [
            segment.strip()
            for segment in segments
            if segment.strip()
        ]

    def _extract_structural_headings(
        self,
        prefix: str,
    ) -> list[str]:
        """Extract the current structural heading context before a candidate."""

        if not prefix.strip():
            return []

        lines = self._prepare_lines(
            prefix
        )

        if not lines:
            return []

        headings: list[str] = []

        for line in lines:
            segments = self._split_structural_segments(
                line
            )

            for segment in segments:
                if self._looks_like_heading(
                    segment
                ):
                    headings = [segment]

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

        for index, line in enumerate(lines):
            if not body_lines:
                if self._looks_like_heading(
                    line
                ):
                    headings.append(
                        line
                    )
                    continue

                if (
                    index + 1 < len(lines)
                    and self._QUESTION_PATTERN.search(
                        lines[index + 1]
                    )
                ):
                    continue

            body_lines.append(
                line
            )

        if not body_lines:
            return headings, ""

        return (
            headings,
            " ".join(
                body_lines
            ),
        )


    def _prepare_lines(
        self,
        text: str,
    ) -> list[str]:
        """Normalize source lines while preserving useful boundaries."""

        raw_lines = text.splitlines()

        lines: list[str] = []
        in_activity_block = False

        for index, raw_line in enumerate(raw_lines):
            normalized = (
                self._normalize_layout_text(
                    raw_line
                )
            )

            if not normalized:
                continue

            if self._is_non_factual_source_line(
                normalized
            ):
                if lines:
                    previous = lines[-1]

                    # A standalone label immediately preceding a
                    # question/activity instruction is not factual
                    # source content.
                    if (
                        index > 0
                        and previous
                        and len(previous.split()) <= 3
                        and not previous.endswith(
                            (".", "!", "?")
                        )
                    ):
                        lines.pop()

                in_activity_block = True
                continue

            if in_activity_block:
                if self._is_activity_continuation(
                    normalized
                ):
                    continue

                in_activity_block = False

            lines.append(
                normalized
            )

        return lines


    def _normalize_source_layout(
        self,
        text: str,
    ) -> str:
        """Normalize common PDF and OCR layout artifacts."""

        if not text:
            return ""

        lines = [
            self._normalize_layout_text(
                line
            )
            for line in text.splitlines()
        ]

        lines = [
            line
            for line in lines
            if line
        ]

        return "\n".join(
            lines
        )

    def _normalize_layout_text(
        self,
        text: str,
    ) -> str:
        """Normalize OCR separators and layout whitespace."""

        value = text.strip()

        if not value:
            return ""

        if self._looks_like_character_spaced_text(
            value
        ):
            value = (
                self._collapse_character_spaced_text(
                    value
                )
            )

        value = re.sub(
            r"^[Æ●•▪◦‣]\s*",
            "",
            value,
        )

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

            result.append(
                part.strip()
            )

        value = "".join(
            result
        )

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

        normalized_heading = (
            self._normalize_layout_text(
                heading
            )
        )

        if not normalized_heading:
            return context

        if not context:
            return [
                normalized_heading
            ]

        if (
            context[-1]
            == normalized_heading
        ):
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
            if (
                not result
                or result[-1] != value
            ):
                result.append(
                    value
                )

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

        if self._PAGE_NUMBER_PATTERN.fullmatch(
            value
        ):
            return False

        if self._QUESTION_PATTERN.search(
            value
        ):
            return False

        if len(value) > 120:
            return False

        words = value.split()

        if not words:
            return False

        if len(words) > 12:
            return False

        if value.endswith(
            (".", "!", "?")
        ):
            return False

        lower = value.lower()

        # Obvious prose/instruction prefixes.
        prose_prefixes = (
            "it ",
            "this ",
            "these ",
            "there ",
            "they ",
            "unlike ",
            "according to ",
            "when ",
            "where ",
            "which ",
            "that ",
            "because ",
            "although ",
            "while ",
            "for ",
            "from ",
            "with ",
        )

        if lower.startswith(
            prose_prefixes
        ):
            return False

        # Obvious PDF/layout artifacts.
        if lower.startswith(
            (
                "chapter ",
                "fig.",
                "figure ",
                "page ",
            )
        ):
            return False

        # Structural separators are strong heading signals.
        if ":" in value:
            return True

        if "|" in value:
            return True


         # Parenthesized suffixes often indicate structural metadata.
        if (
            value.endswith(")")
            and "(" in value
        ):
            return True

        # Short all-uppercase text is commonly a heading.
        if (
            value.isupper()
            and len(words) <= 10
        ):
            return True



        # Title-case text is a useful heading signal.
        capitalized_words = sum(
            1
            for word in words
            if word
            and word[0].isupper()
        )

        return (
            capitalized_words
            >= max(
                2,
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

        if re.fullmatch(
            r"(?:fig\.?|figure|chapter|page)\s*\d*(?:\.\d+)?",
            lower,
        ):
            return True

        if re.match(
            r"^chapter\s+\d+\.indd",
            lower,
        ):
            return True

        if re.match(
            r"^\d+\.\s+",
            normalized,
        ):
            return True

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
            "what precautionary ",
            "what ",
            "how ",
        )

        if lower.startswith(
            instruction_prefixes
        ):
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
        """Return whether source is primarily a textbook activity page."""

        normalized = self._normalize_whitespace(
            source
        )

        if not normalized:
            return True

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

        return (
            question_count > 0
            and instruction_count >= 2
        )