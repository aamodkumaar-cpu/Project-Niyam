"""
Knowledge Extractor.

Type:
    Domain Service

Purpose:
    Select source-grounded knowledge from deterministic source candidates.

Responsibilities:
    - Build deterministic source candidates.
    - Ask the LLM which candidates answer the question.
    - Parse candidate selections.
    - Resolve selected IDs back to original source fragments.
    - Enforce exhaustive-request coverage.
    - Enforce explicit maximum facts per heading.
    - Validate source grounding.
    - Produce StructuredKnowledge.

Does NOT:
    - Retrieve knowledge.
    - Generate source wording.
    - Rewrite facts.
    - Answer user questions.
    - Perform semantic similarity.
"""

from __future__ import annotations

import re

from backend.diagnostic.ExecutionDebuggerContract import (
    ExecutionDebuggerContract,
)
from backend.extraction.ExtractionCandidate import ExtractionCandidate
from backend.extraction.ExtractionCandidateBuilder import (
    ExtractionCandidateBuilder,
)
from backend.extraction.ExtractionPromptBuilder import (
    ExtractionPromptBuilder,
)
from backend.extraction.ExtractionResponseParser import (
    ExtractionResponseParser,
    ExtractionSelection,
)
from backend.extraction.KnowledgeFact import KnowledgeFact
from backend.extraction.KnowledgeSchema import KnowledgeSchema
from backend.extraction.SourceQuoteValidator import (
    SourceQuoteValidator,
)
from backend.extraction.StructuredKnowledge import StructuredKnowledge
from backend.llm.LLMClient import LLMClient
from backend.llm.Message import Messages
from backend.retrieval.KnowledgeNode import KnowledgeNode


class KnowledgeExtractor:
    """Selects structured knowledge from deterministic source candidates."""

    def __init__(
        self,
        prompt_builder: ExtractionPromptBuilder,
        llm_client: LLMClient,
        execution_debugger: ExecutionDebuggerContract,
        knowledge_schema: KnowledgeSchema,
        source_quote_validator: SourceQuoteValidator,
        response_parser: ExtractionResponseParser,
        candidate_builder: ExtractionCandidateBuilder,
    ) -> None:
        """Initialize the knowledge extractor."""

        self.prompt_builder = prompt_builder
        self.llm_client = llm_client
        self.execution_debugger = execution_debugger
        self.knowledge_schema = knowledge_schema
        self.source_quote_validator = source_quote_validator
        self.response_parser = response_parser
        self.candidate_builder = candidate_builder

    def extract(
        self,
        question: str,
        knowledge_nodes: list[KnowledgeNode],
    ) -> StructuredKnowledge:
        """Select and return only source-grounded knowledge."""

        candidates = self.candidate_builder.build(
            knowledge_nodes
        )

        if not candidates:
            return StructuredKnowledge()

        messages: Messages = self.prompt_builder.build(
            question=question,
            candidates=candidates,
        )

        self.execution_debugger.prompt(
            messages
        )

        response = self.llm_client.generate(
            messages=messages,
            response_format=self.knowledge_schema.json_schema(),
        )

        self.execution_debugger.raw_llm_response(
            title="Knowledge Selection",
            response=response,
        )

        selections = self.response_parser.parse(
            response
        )

        knowledge = self._build_structured_knowledge(
            selections=selections,
            candidates=candidates,
            question=question,
        )

        self.execution_debugger.extraction(
            knowledge
        )

        return knowledge

    def _build_structured_knowledge(
        self,
        selections: list[ExtractionSelection],
        candidates: list[ExtractionCandidate],
        question: str,
    ) -> StructuredKnowledge:
        """Resolve selected IDs and enforce deterministic constraints."""

        candidate_map = {
            candidate.candidate_id: candidate
            for candidate in candidates
        }

        max_per_heading = (
            self._extract_max_per_heading(
                question
            )
        )

        exhaustive = self._is_exhaustive_request(
            question
        )

        knowledge = StructuredKnowledge()

        selected_ids: set[str] = set()
        heading_counts: dict[str, int] = {}

        # --------------------------------------------------------------
        # Phase 1:
        # Accept valid LLM selections.
        # --------------------------------------------------------------

        for selection in selections:
            candidate_id = selection["candidate_id"]

            if candidate_id in selected_ids:
                continue

            candidate = candidate_map.get(
                candidate_id
            )

            if candidate is None:
                continue

            heading = self._candidate_heading(
                candidate
            )

            count = heading_counts.get(
                heading,
                0,
            )

            if (
                max_per_heading is not None
                and count >= max_per_heading
            ):
                continue

            if self._is_ambiguous_candidate(
                candidate=candidate,
                candidates=candidates,
            ):
                self._reject(
                    candidate=candidate,
                    confidence=selection["confidence"],
                )
                continue

            if not self.source_quote_validator.is_supported(
                source_quote=candidate.source_quote,
                source_text=candidate.node.content,
            ):
                self._reject(
                    candidate=candidate,
                    confidence=selection["confidence"],
                )
                continue

            fact = KnowledgeFact(
                name=heading,
                value=candidate.source_quote,
                source=candidate.node.metadata.source,
                page_number=candidate.node.metadata.page_number,
                confidence=selection["confidence"],
            )

            if self._is_duplicate(
                fact=fact,
                knowledge=knowledge,
            ):
                continue

            knowledge.facts.append(
                fact
            )

            selected_ids.add(
                candidate_id
            )

            heading_counts[heading] = (
                count + 1
            )

        # --------------------------------------------------------------
        # Phase 2:
        # Exhaustive requests are completed deterministically.
        #
        # The LLM can select relevant evidence, but it cannot make
        # an "all/every/each" request incomplete.
        # --------------------------------------------------------------

        if exhaustive:
            self._complete_exhaustive_selection(
                candidates=candidates,
                knowledge=knowledge,
                selected_ids=selected_ids,
                heading_counts=heading_counts,
                max_per_heading=max_per_heading,
            )

        return knowledge

    def _complete_exhaustive_selection(
        self,
        candidates: list[ExtractionCandidate],
        knowledge: StructuredKnowledge,
        selected_ids: set[str],
        heading_counts: dict[str, int],
        max_per_heading: int | None,
    ) -> None:
        """Complete every represented professional-experience heading."""

        if max_per_heading is None:
            return

        experience_headings: list[str] = []

        for candidate in candidates:
            heading = self._candidate_heading(
                candidate
            )

            if not heading:
                continue

            if not self._is_experience_heading(
                heading
            ):
                continue

            if heading not in experience_headings:
                experience_headings.append(
                    heading
                )

        for heading in experience_headings:
            current_count = heading_counts.get(
                heading,
                0,
            )

            if current_count >= max_per_heading:
                continue

            for candidate in candidates:
                if (
                    self._candidate_heading(
                        candidate
                    )
                    != heading
                ):
                    continue

                if (
                    candidate.candidate_id
                    in selected_ids
                ):
                    continue

                if current_count >= max_per_heading:
                    break

                if self._is_ambiguous_candidate(
                    candidate=candidate,
                    candidates=candidates,
                ):
                    continue

                if not self.source_quote_validator.is_supported(
                    source_quote=candidate.source_quote,
                    source_text=candidate.node.content,
                ):
                    continue

                fact = KnowledgeFact(
                    name=heading,
                    value=candidate.source_quote,
                    source=candidate.node.metadata.source,
                    page_number=candidate.node.metadata.page_number,
                    confidence=1.0,
                )

                if self._is_duplicate(
                    fact=fact,
                    knowledge=knowledge,
                ):
                    selected_ids.add(
                        candidate.candidate_id
                    )
                    continue

                knowledge.facts.append(
                    fact
                )

                selected_ids.add(
                    candidate.candidate_id
                )

                current_count += 1
                heading_counts[heading] = (
                    current_count
                )

    def _is_exhaustive_request(
        self,
        question: str,
    ) -> bool:
        """Return whether the question requests broad coverage."""

        normalized = question.lower()

        exhaustive_terms = (
            "all ",
            "all the ",
            "each ",
            "every ",
            "from all ",
            "from each ",
            "from every ",
        )

        return any(
            term in normalized
            for term in exhaustive_terms
        )

    def _extract_max_per_heading(
        self,
        question: str,
    ) -> int | None:
        """Extract an explicit maximum-per-heading constraint."""

        patterns = (
            r"\bmax(?:imum)?\s+(\d+)\s+"
            r"(?:bullet\s+points?|points?|items?)",
            r"\bup\s+to\s+(\d+)\s+"
            r"(?:bullet\s+points?|points?|items?)",
        )

        for pattern in patterns:
            match = re.search(
                pattern,
                question,
                flags=re.IGNORECASE,
            )

            if match is not None:
                return int(
                    match.group(1)
                )

        return None

    def _candidate_heading(
        self,
        candidate: ExtractionCandidate,
    ) -> str:
        """Return the candidate's structural heading."""

        heading = candidate.heading.strip()

        if heading:
            return heading

        return candidate.node.metadata.source

    def _is_experience_heading(
        self,
        heading: str,
    ) -> bool:
        """Return whether a heading represents professional experience."""

        value = " ".join(
            heading.split()
        ).strip()

        if not value:
            return False

        upper = value.upper()

        if "EARLY CAREER" in upper:
            return True

        if "(" not in value:
            return False

        if ")" not in value:
            return False

        if not re.search(
            r"\b(?:19|20)\d{2}\b",
            value,
        ):
            return False

        excluded = (
            "EDUCATION",
            "CERTIFICATION",
            "CERTIFICATIONS",
        )

        return not any(
            item in upper
            for item in excluded
        )

    def _is_ambiguous_candidate(
        self,
        candidate: ExtractionCandidate,
        candidates: list[ExtractionCandidate],
    ) -> bool:
        """Return whether identical evidence exists at multiple locations."""

        normalized_quote = " ".join(
            candidate.source_quote.split()
        )

        identities = {
            (
                other.node.metadata.document_id,
                other.node.metadata.page_number,
                other.node.metadata.chunk_number,
            )
            for other in candidates
            if " ".join(
                other.source_quote.split()
            ) == normalized_quote
        }

        return len(identities) > 1

    def _is_duplicate(
        self,
        fact: KnowledgeFact,
        knowledge: StructuredKnowledge,
    ) -> bool:
        """Return whether an equivalent source fact is already present."""

        return any(
            existing.name == fact.name
            and existing.value == fact.value
            and existing.source == fact.source
            and existing.page_number == fact.page_number
            for existing in knowledge.facts
        )

    def _reject(
        self,
        candidate: ExtractionCandidate,
        confidence: float,
    ) -> None:
        """Record a rejected candidate for diagnostics."""

        self.execution_debugger.rejected_fact(
            KnowledgeFact(
                name=self._candidate_heading(
                    candidate
                ),
                value=candidate.source_quote,
                source=candidate.node.metadata.source,
                page_number=candidate.node.metadata.page_number,
                confidence=confidence,
            )
        )