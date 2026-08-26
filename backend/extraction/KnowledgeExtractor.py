"""
Knowledge Extractor.

Type:

    Domain Service

Purpose:

    Select source-grounded knowledge from deterministic extraction candidates.

Responsibilities:

    - Analyze extraction question constraints.
    - Build deterministic extraction candidates.
    - Rank candidates at fact level.
    - Ask the LLM to select supporting candidates.
    - Validate selected source evidence.
    - Enforce deterministic extraction constraints.
    - Produce structured knowledge.

Does NOT:

    - Retrieve knowledge.
    - Generate final natural-language answers.
    - Invent factual content.
"""

from __future__ import annotations

from backend.diagnostic.ExecutionDebuggerContract import ExecutionDebuggerContract
from backend.extraction.ExtractionCandidate import ExtractionCandidate
from backend.extraction.ExtractionCandidateBuilder import (
    ExtractionCandidateBuilder,
)
from backend.extraction.ExtractionCandidateRanker import (
    ExtractionCandidateRanker,
)
from backend.extraction.ExtractionQuestionAnalyzer import (
    ExtractionQuestionAnalyzer,
)
from backend.extraction.ExtractionResponseParser import (
    ExtractionResponseParser,
    ExtractionSelection,
)
from backend.extraction.KnowledgeFact import KnowledgeFact
from backend.extraction.KnowledgeSchema import KnowledgeSchema
from backend.extraction.SourceQuoteValidator import SourceQuoteValidator
from backend.llm.LLMClient import LLMClient
from backend.llm.Message import Messages
from backend.retrieval.KnowledgeNode import KnowledgeNode
from backend.extraction.StructuredKnowledge import StructuredKnowledge



class KnowledgeExtractor:
    """Selects structured knowledge from deterministic source candidates."""

    def __init__(
        self,
        prompt_builder,
        llm_client: LLMClient,
        execution_debugger: ExecutionDebuggerContract,
        knowledge_schema: KnowledgeSchema,
        source_quote_validator: SourceQuoteValidator,
        response_parser: ExtractionResponseParser,
        candidate_builder: ExtractionCandidateBuilder,
        question_analyzer: ExtractionQuestionAnalyzer,
        candidate_ranker: ExtractionCandidateRanker,
    ) -> None:
        """Initialize the knowledge extractor."""

        self.prompt_builder = prompt_builder
        self.llm_client = llm_client
        self.execution_debugger = execution_debugger
        self.knowledge_schema = knowledge_schema
        self.source_quote_validator = source_quote_validator
        self.response_parser = response_parser
        self.candidate_builder = candidate_builder
        self.question_analyzer = question_analyzer
        self.candidate_ranker = candidate_ranker

    def extract(
        self,
        question: str,
        knowledge_nodes: list[KnowledgeNode],
    ) -> StructuredKnowledge:
        """Select and return only source-grounded knowledge."""

        relationship = (
            self.question_analyzer.is_relationship_question(
                question
            )
        )

        role_question = (
            self.question_analyzer.is_role_question(
                question
            )
        )

        candidates = self.candidate_builder.build(
            knowledge_nodes=knowledge_nodes,
            relationship=relationship,
        )

        if not candidates:
            return StructuredKnowledge()

        ranked_candidates = self.candidate_ranker.rank(
            question=question,
            candidates=candidates,
        )

        prompt_candidates = self.candidate_ranker.select_for_prompt(
            question=question,
            candidates=ranked_candidates,
        )

        messages: Messages = self.prompt_builder.build(
            question=question,
            candidates=prompt_candidates,
        )

        self.execution_debugger.prompt(
            messages
        )

        response = self.llm_client.generate(
            messages=messages,
        )

        self.execution_debugger.raw_llm_response(
            title="Knowledge Selection",
            response=response,
        )

        selections = self.response_parser.parse(
            response
        )

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
            role_question=role_question,
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
        role_question: bool,
    ) -> StructuredKnowledge:
        """Resolve selections and enforce deterministic extraction constraints."""

        candidate_map = {
            candidate.candidate_id: candidate
            for candidate in candidates
        }

        maximum = (
            self.question_analyzer.extract_max_per_heading(
                question
            )
        )

        exhaustive = (
            self.question_analyzer.is_exhaustive_request(
                question
            )
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
            role_question=role_question,
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
        role_question: bool,
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
                value=(
                    self._candidate_heading(candidate)
                    if role_question
                    else candidate.source_quote
                ),
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
        value: str | None = None,
    ) -> KnowledgeFact:
        """Create a source-grounded knowledge fact from a candidate."""

        return KnowledgeFact(
            name=self._candidate_heading(
                candidate
            ),
            value=(
                value
                if value is not None
                else candidate.source_quote
            ),
            source=candidate.node.metadata.source,
            page_number=candidate.node.metadata.page_number,
            confidence=confidence,
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