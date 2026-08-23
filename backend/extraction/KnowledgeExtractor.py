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
    - Enforce exhaustive request coverage.
    - Enforce explicit maximum facts per heading.
    - Validate source grounding.
    - Produce StructuredKnowledge.

Does NOT:
    - Retrieve knowledge.
    - Contain domain-specific business rules.
    - Interpret resumes, companies, vendors, or other domain entities.
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
from backend.extraction.ExtractionCandidate import (
    ExtractionCandidate,
)
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
from backend.extraction.KnowledgeFact import (
    KnowledgeFact,
)
from backend.extraction.KnowledgeSchema import (
    KnowledgeSchema,
)
from backend.extraction.SourceQuoteValidator import (
    SourceQuoteValidator,
)
from backend.extraction.StructuredKnowledge import (
    StructuredKnowledge,
)
from backend.llm.LLMClient import (
    LLMClient,
)
from backend.llm.Message import (
    Messages,
)
from backend.retrieval.KnowledgeNode import (
    KnowledgeNode,
)


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

        relationship = self.prompt_builder._is_relationship_question(
            question
        )

        candidates = self.candidate_builder.build(
            knowledge_nodes,
            relationship=relationship,
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

        # ZERO-SELECTION means there is no source-supported answer.
        # Do not allow any downstream component to fall back to
        # retrieved-but-unselected knowledge.
        if not selections:
            knowledge = StructuredKnowledge()

            self.execution_debugger.extraction(
                knowledge
            )

            return knowledge

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
        """Resolve selections and enforce deterministic extraction constraints."""

        candidate_map = {
            candidate.candidate_id: candidate
            for candidate in candidates
        }

        maximum = self._extract_max_per_heading(
            question
        )

        exhaustive = self._is_exhaustive_request(
            question
        )

        knowledge = StructuredKnowledge()

        selected_ids: set[str] = set()
        heading_counts: dict[str, int] = {}

        self._accept_llm_selections(
            selections=selections,
            candidates=candidates,
            candidate_map=candidate_map,
            knowledge=knowledge,
            selected_ids=selected_ids,
            heading_counts=heading_counts,
            maximum=maximum,
        )

        if exhaustive:
            self._complete_exhaustive_selection(
                candidates=candidates,
                knowledge=knowledge,
                selected_ids=selected_ids,
                heading_counts=heading_counts,
                maximum=maximum,
            )

        return knowledge

    def _accept_llm_selections(
        self,
        selections: list[ExtractionSelection],
        candidates: list[ExtractionCandidate],
        candidate_map: dict[str, ExtractionCandidate],
        knowledge: StructuredKnowledge,
        selected_ids: set[str],
        heading_counts: dict[str, int],
        maximum: int | None,
    ) -> None:
        """Accept valid candidates selected by the LLM."""

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
                maximum is not None
                and count >= maximum
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

            fact = self._create_fact(
                candidate=candidate,
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

    def _complete_exhaustive_selection(
        self,
        candidates: list[ExtractionCandidate],
        knowledge: StructuredKnowledge,
        selected_ids: set[str],
        heading_counts: dict[str, int],
        maximum: int | None,
    ) -> None:
        """Complete exhaustive requests across every represented heading."""

        headings: list[str] = []

        for candidate in candidates:
            heading = self._candidate_heading(
                candidate
            )

            if heading not in headings:
                headings.append(
                    heading
                )

        for heading in headings:
            current_count = heading_counts.get(
                heading,
                0,
            )

            if (
                maximum is not None
                and current_count >= maximum
            ):
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

                if (
                    maximum is not None
                    and current_count >= maximum
                ):
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

                fact = self._create_fact(
                    candidate=candidate,
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

    def _create_fact(
        self,
        candidate: ExtractionCandidate,
        confidence: float,
    ) -> KnowledgeFact:
        """Create a source-grounded knowledge fact from a candidate."""

        return KnowledgeFact(
            name=self._candidate_heading(
                candidate
            ),
            value=candidate.source_quote,
            source=candidate.node.metadata.source,
            page_number=candidate.node.metadata.page_number,
            confidence=confidence,
        )

    def _extract_max_per_heading(
        self,
        question: str,
    ) -> int | None:
        """Extract an explicit maximum-per-heading constraint."""

        patterns = (
            r"\b(?:only|exactly)\s+(\d+)\s+"
            r"(?:bullet\s+points?|points?|items?)\b",
            r"\b(?:max(?:imum)?|up\s+to)\s+(\d+)\s+"
            r"(?:bullet\s+points?|points?|items?)\b",
        )

        for pattern in patterns:
            match = re.search(
                pattern,
                question,
                flags=re.IGNORECASE,
            )

            if match is not None:
                maximum = int(
                    match.group(1)
                )

                if maximum > 0:
                    return maximum

        return None

    def _is_exhaustive_request(
        self,
        question: str,
    ) -> bool:
        """Return whether the question requests exhaustive coverage."""

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

    def _candidate_heading(
        self,
        candidate: ExtractionCandidate,
    ) -> str:
        """Return the candidate's structural heading."""

        heading = candidate.heading.strip()

        if heading:
            return heading

        return candidate.node.metadata.source

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