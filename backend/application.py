"""
Project-Niyam Application Composition Root

Responsible for wiring all application components together.
"""
from backend.compliance.BusinessProfile import BusinessProfile
from backend.compliance.BusinessProfileExtractor import BusinessProfileExtractor
from backend.compliance.ComplianceChecklistService import ComplianceChecklistService
from backend.ingestion.KnowledgeDomain import KnowledgeDomain
from backend.intents.IntentClassifier import IntentClassifier
from backend.intents.IntentType import IntentType
from backend.retrieval.SemanticRetrievalService import SemanticRetrievalService
from backend.retrieval.KeywordRetrievalService import KeywordRetrievalService
from backend.retrieval.ResultMerger import ResultMerger

from backend.ingestion.EmbeddingService import EmbeddingService
from backend.retrieval.VectorRepository import VectorRepository
from backend.retrieval.RetrievalService import RetrievalService
from backend.prompt.PromptBuilder import PromptBuilder
from backend.llm.OllamaService import OllamaService
from backend.diagnostic.RetrievalInspector import RetrievalInspector
from backend.diagnostic.PromptInspector import PromptInspector
from backend.results.AnswerResult import AnswerResult


class Application:

    def __init__(self):

        self.embedding_service = EmbeddingService()
        self.vector_repository = VectorRepository()

        self.semantic_retrieval_service = SemanticRetrievalService(
            embedding_service=self.embedding_service,
            vector_repository=self.vector_repository
        )

        self.keyword_retrieval_service = KeywordRetrievalService(
            vector_repository=self.vector_repository
        )

        self.result_merger = ResultMerger()

        self.retrieval_service = RetrievalService(
            semantic_retrieval_service=self.semantic_retrieval_service,
            keyword_retrieval_service=self.keyword_retrieval_service,
            result_merger=self.result_merger
        )
        self.prompt_builder = PromptBuilder()
        self.ollama_service = OllamaService()

        self.compliance_checklist_service = ComplianceChecklistService()
        self.intent_classifier = IntentClassifier()

        self.business_profile_extractor = BusinessProfileExtractor()

    def detect_intent(
        self,
        question: str
    ):
        """Detect the user's intent."""

        return self.intent_classifier.classify(
            question
        )


    def search(
        self,
        question: str,
        where: dict | None = None,
        domain: KnowledgeDomain | None = None
    ) -> AnswerResult:
        """Search the knowledge base and generate an answer."""

        intent = self.detect_intent(question)

        if intent.type == IntentType.COMPLIANCE_CHECKLIST:
            business_profile = self.business_profile_extractor.extract(
                question
            )
            checklist = self.generate_compliance_checklist(
                business_profile
            )

            answer = "\n".join(
                item.title
                for item in checklist.items
            )

            return AnswerResult(
                answer=answer,
                sources=[]
            )

        if domain:
            where = {
                "domain": domain.value
            }
            
        knowledge_nodes = self.retrieval_service.retrieve( 
            question=question,
            where=where
        )

        RetrievalInspector.inspect(
            question,
            knowledge_nodes
        )

        messages = self.prompt_builder.build(
            question=question,
            knowledge_nodes=knowledge_nodes
        )
        PromptInspector.inspect(messages)
        answer = self.ollama_service.generate(messages)

        # sources = []
        # for node in knowledge_nodes:
        #     sources.append(node.metadata)
        sources = [node.metadata for node in knowledge_nodes]

        return AnswerResult(
            answer=answer,
            sources=sources
        )


    def generate_compliance_checklist(
        self,
         business_profile: BusinessProfile
    ):
        """Generate a compliance checklist."""

        return self.compliance_checklist_service.generate(
            business_profile
        )