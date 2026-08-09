# Changelog

All notable changes to Project Niyam will be documented in this file.

The format follows Semantic Versioning.

---

## [Unreleased]

---

## [v0.5.0] - 2026-07-31

### Added
- NiyamAgent orchestration layer
- ExecutionPlanner
- ExecutionPlan
- ExecutionStep
- ExecutionExecutor
- ExecutionContext
- ExecutionResult
- ExecutionTrace
- ExecutionMonitor
- Tool abstraction
- ToolRegistry
- KnowledgeSearchTool
- ComplianceChecklistTool
- ResponseBuilder
- ConversationMemory foundation
- KnowledgeSearchService
- KnowledgeSearchResult

### Changed
- Refactored request processing into Agent → Planner → Executor → Tool pipeline
- Knowledge search migrated to Tool-based architecture
- Compliance checklist integrated into the execution pipeline
- Added execution monitoring and tracing
- Introduced workflow execution foundation for future multi-step plans

---

## [v0.2.0] - 2026-07-15

### Added
- Hybrid Retrieval architecture
- Semantic Retrieval Service
- Keyword Retrieval Service
- Result Merger
- Retrieval Inspector
- Prompt Inspector
- Chunk Inspector

### Improved
- Refactored RetrievalService
- Introduced Repository pattern
- Improved type safety
- Improved project structure
- Added manual testing documentation

---

## [v0.1.0] - 2026-07-05

### Added
- Initial Project Niyam prototype
- PDF ingestion
- Text chunking
- Embedding generation
- ChromaDB integration
- Semantic search
- Prompt Builder
- Ollama integration
- Interactive CLI