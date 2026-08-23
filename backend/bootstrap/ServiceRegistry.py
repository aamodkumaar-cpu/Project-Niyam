"""
Service Registry.

Type:
    Composition Root

Purpose:
    Creates and wires the complete Project Niyam object graph.

Responsibilities:
    - Create shared services
    - Wire dependencies
    - Register tools
    - Expose configured application components

Does NOT:
    - Execute business logic
    - Perform orchestration
    - Retrieve knowledge
    - Call the LLM
"""

from backend.agent.NiyamAgent import NiyamAgent
from backend.compliance.BusinessProfileSession import BusinessProfileSession
from backend.config.settings import DOCUMENTS_DIR
from backend.extraction.AnswerGenerator import AnswerGenerator
from backend.extraction.AnswerPromptBuilder import AnswerPromptBuilder
from backend.extraction.ExtractionResponseParser import ExtractionResponseParser
from backend.extraction.SourceQuoteValidator import SourceQuoteValidator
from backend.ingestion.DocumentCatalogRepository import DocumentCatalogRepository
from backend.ingestion.DocumentService import DocumentService
from backend.ingestion.IngestionService import IngestionService
from backend.orchestration.ExecutionExecutor import ExecutionExecutor
from backend.orchestration.RequestRouter import RequestRouter
from backend.presentation.AnswerFormatterService import AnswerFormatterService
from backend.prompt.ContextAssembler import ContextAssembler
from backend.prompt.ContextOrganizer import ContextOrganizer
from backend.retrieval.KeywordRankingStrategy import KeywordRankingStrategy
from backend.retrieval.KeywordRetrievalService import KeywordRetrievalService
from backend.retrieval.KeywordScorer import KeywordScorer
from backend.retrieval.KeywordTokenizer import KeywordTokenizer
from backend.retrieval.KnowledgeSearchService import KnowledgeSearchService
from backend.retrieval.QuestionNormalizer import QuestionNormalizer
from backend.retrieval.RankingStrategy import RankingStrategy
from backend.retrieval.RelevanceFilter import RelevanceFilter
from backend.retrieval.ResultMerger import ResultMerger
from backend.retrieval.RetrievalPipeline import RetrievalPipeline
from backend.retrieval.RetrievalService import RetrievalService
from backend.retrieval.RetrievalStrategy import RetrievalStrategy
from backend.retrieval.SemanticRetrievalService import SemanticRetrievalService
from backend.tools.AnswerFormatterTool import AnswerFormatterTool
from backend.tools.KnowledgeSearchTool import KnowledgeSearchTool
from backend.tools.ToolRegistry import ToolRegistry
from backend.compliance.ComplianceChecklistService import ComplianceChecklistService
from backend.tools.ComplianceChecklistTool import ComplianceChecklistTool
from backend.orchestration.ExecutionMonitor import ExecutionMonitor
from backend.ingestion.EmbeddingService import EmbeddingService
from backend.llm.OllamaService import OllamaService
from backend.memory.ConversationMemory import ConversationMemory
from backend.orchestration.ExecutionPlanner import ExecutionPlanner
from backend.presentation.ResponseBuilder import ResponseBuilder
from backend.retrieval.VectorRepository import VectorRepository
from backend.intents.IntentClassifier import IntentClassifier
from backend.retrieval.CandidateFilter import CandidateFilter
from backend.extraction.KnowledgeExtractor import KnowledgeExtractor
from backend.extraction.ExtractionPromptBuilder import ExtractionPromptBuilder
from backend.extraction.ExtractionCandidateBuilder import ExtractionCandidateBuilder
from backend.extraction.KnowledgeSchema import KnowledgeSchema
from backend.diagnostic.ConsoleLogger import ConsoleLogger
from backend.diagnostic.ExecutionDebugger import ExecutionDebugger
from backend.diagnostic.LogLevel import LogLevel


class ServiceRegistry:
    """Creates and wires the application object graph."""

    logger: ConsoleLogger
    execution_debugger: ExecutionDebugger

    knowledge_extractor: KnowledgeExtractor
    candidate_filter: CandidateFilter
    tool_registry: ToolRegistry
    embedding_service: EmbeddingService
    vector_repository: VectorRepository

    keyword_tokenizer: KeywordTokenizer
    keyword_scorer: KeywordScorer

    context_organizer: ContextOrganizer

    business_profile_session: BusinessProfileSession
    ollama_service: OllamaService
    answer_generator: AnswerGenerator

    retrieval_pipeline: RetrievalPipeline
    knowledge_search_service: KnowledgeSearchService

    answer_formatter_service: AnswerFormatterService
    compliance_checklist_service: ComplianceChecklistService

    execution_monitor: ExecutionMonitor

    intent_classifier: IntentClassifier
    execution_planner: ExecutionPlanner
    execution_executor: ExecutionExecutor

    response_builder: ResponseBuilder
    conversation_memory: ConversationMemory

    niyam_agent: NiyamAgent
    request_router: RequestRouter

    document_repository: DocumentCatalogRepository
    document_service: DocumentService
    ingestion_service: IngestionService
    context_assembler: ContextAssembler

    def __init__(self) -> None:
        """Create the complete application object graph."""

        self.tool_registry = ToolRegistry()

        self._create_infrastructure()
        self._create_ingestion()
        self._create_retrieval()
        self._create_services()
        self._register_tools()
        self._create_execution()
        self._create_agent()
        self._create_router()



    def _create_infrastructure(self) -> None:
        """Create shared infrastructure services."""

        self.logger = ConsoleLogger(
            level=LogLevel.DEBUG
        )

        self.execution_debugger = ExecutionDebugger(
            logger=self.logger
        )

        self.embedding_service = EmbeddingService()

        self.keyword_tokenizer = KeywordTokenizer()
        self.keyword_scorer = KeywordScorer()

        self.vector_repository = VectorRepository(
            keyword_tokenizer=self.keyword_tokenizer,
            keyword_scorer=self.keyword_scorer,
        )

        self.context_organizer = ContextOrganizer()

        self.context_assembler = ContextAssembler(
            context_organizer=self.context_organizer
        )

        self.ollama_service = OllamaService()

        knowledge_schema = KnowledgeSchema()

        extraction_prompt_builder = ExtractionPromptBuilder()

        source_quote_validator = SourceQuoteValidator()

        response_parser = ExtractionResponseParser()

        candidate_builder = ExtractionCandidateBuilder()

        self.knowledge_extractor = KnowledgeExtractor(
            prompt_builder=extraction_prompt_builder,
            llm_client=self.ollama_service,
            execution_debugger=self.execution_debugger,
            knowledge_schema=knowledge_schema,
            source_quote_validator=source_quote_validator,
            response_parser=response_parser,
            candidate_builder=candidate_builder,
        )

        self.answer_generator = AnswerGenerator(
                prompt_builder=AnswerPromptBuilder(),
                llm_client=self.ollama_service,
            )

        self.execution_monitor = ExecutionMonitor()

        self.intent_classifier = IntentClassifier()

        self.execution_planner = ExecutionPlanner()

        self.response_builder = ResponseBuilder()

        self.conversation_memory = ConversationMemory()

        self.answer_formatter_service = AnswerFormatterService()

        self.compliance_checklist_service = ComplianceChecklistService()

        self.business_profile_session = BusinessProfileSession()

        self.candidate_filter = CandidateFilter()



    def _create_retrieval(self) -> None:
        """Create the retrieval pipeline."""

        semantic_retrieval_service = SemanticRetrievalService(
            embedding_service=self.embedding_service,
            vector_repository=self.vector_repository,
        )

        keyword_retrieval_service = KeywordRetrievalService(
            vector_repository=self.vector_repository,
        )

        retrieval_strategies: list[RetrievalStrategy] = [
            semantic_retrieval_service,
            keyword_retrieval_service,
        ]

        ranking_strategies: list[RankingStrategy] = [
            KeywordRankingStrategy(
                keyword_tokenizer=self.keyword_tokenizer,
                keyword_scorer=self.keyword_scorer,
            ),
        ]

        relevance_filter = RelevanceFilter(minimum_score=0.0,)

        retrieval_service = RetrievalService(
            retrieval_strategies=retrieval_strategies,
            ranking_strategies=ranking_strategies,
            result_merger=ResultMerger(),
            relevance_filter=relevance_filter,
        )

        question_normalizer = QuestionNormalizer()

        self.retrieval_pipeline = RetrievalPipeline(
            retrieval_service=retrieval_service,
            question_normalizer=question_normalizer,
            candidate_filter=self.candidate_filter,
        )





    def _create_services(self) -> None:
        """Create domain services."""

        self.knowledge_search_service = KnowledgeSearchService(
            retrieval_pipeline=self.retrieval_pipeline,
            knowledge_extractor=self.knowledge_extractor,
            answer_generator=self.answer_generator,
            execution_debugger=self.execution_debugger
        )

    def _register_tools(self) -> None:
        """Register all application tools."""

        self.tool_registry.register(
            KnowledgeSearchTool(
                service=self.knowledge_search_service
            )
        )

        self.tool_registry.register(
            ComplianceChecklistTool(
                service=self.compliance_checklist_service
            )
        )

        self.tool_registry.register(
            AnswerFormatterTool(
                service=self.answer_formatter_service
            )
        )

    def _create_execution(self) -> None:
        """Create the execution layer."""

        self.execution_executor = ExecutionExecutor(
            tool_registry=self.tool_registry,
            execution_monitor=self.execution_monitor
        )

    def _create_agent(self) -> None:
        """Create the Niyam agent."""

        self.niyam_agent = NiyamAgent(
            intent_classifier=self.intent_classifier,
            request_planner=self.execution_planner,
            plan_executor=self.execution_executor,
            response_builder=self.response_builder,
            conversation_memory=self.conversation_memory
        )

    def _create_router(self) -> None:
        """Create the request router."""

        self.request_router = RequestRouter(
            business_profile_session=self.business_profile_session,
            agent=self.niyam_agent
        )

    def _create_ingestion(self) -> None:
        """Create ingestion services."""

        self.document_repository = DocumentCatalogRepository(
            DOCUMENTS_DIR
        )

        self.document_service = DocumentService(
            document_repository=self.document_repository,
            vector_repository=self.vector_repository
        )

        self.ingestion_service = IngestionService(
            embedding_service=self.embedding_service,
            vector_repository=self.vector_repository,
            execution_debugger=self.execution_debugger
        )