# Project Niyam - Ingestion Pipeline

## Purpose

The ingestion pipeline is responsible for converting enterprise documents
into searchable knowledge.

Unlike the retrieval pipeline, ingestion is performed only once for each
document (or whenever the document changes).

The output of this pipeline is stored in the Vector Database.

---

# High-Level Flow

                PDF Document
                      │
                      ▼
                IngestionService
                      │
      ┌───────────────┼────────────────┐
      ▼               ▼                ▼
 PDFReader      TextChunker     EmbeddingService
      │               │                │
      ▼               ▼                ▼
   Pages          Chunks         Embeddings
                      │
                      ▼
             VectorRepository
                      │
                      ▼
                 ChromaDB

---

# Step-by-Step Flow

## Step 1

### IngestionService

Responsibility

Coordinates the complete ingestion workflow.

It does not perform PDF reading, chunking, embedding generation or database
operations itself.

Instead, it orchestrates the workflow by delegating each responsibility to
the appropriate component.

Workflow

1. Read PDF
2. Create chunks
3. Generate embeddings
4. Store everything in ChromaDB

---

## Step 2

### PDFReader

Responsibility

Reads a PDF document and extracts text page by page.

Output

A list of Page objects.

Example

Page 1

- page_number = 1
- text = "..."

Page 2

- page_number = 2
- text = "..."

Why?

Keeping page information allows us to provide source attribution later.

---

## Step 3

### TextChunker

Responsibility

Splits each page into smaller chunks suitable for semantic search.

Input

List of Page objects.

Output

List of Chunk objects.

Each Chunk contains

- chunk text
- page number

Why?

Large documents cannot be embedded efficiently.

Smaller chunks improve retrieval quality and reduce embedding cost.

---

## Step 4

### EmbeddingService

Responsibility

Converts text into numerical vector embeddings.

Input

Chunk text.

Output

Vector embedding.

The service hides the embedding model from the rest of the application.

Today

- Ollama Embeddings

Future

- OpenAI
- Gemini
- VoyageAI
- BGE
- Nomic

Only this class should change.

---

## Step 5

### VectorRepository

Responsibility

Stores searchable knowledge in ChromaDB.

For every chunk it stores

- Chunk text
- Vector embedding
- Metadata

Metadata includes

- document_id
- source
- page_number
- chunk_number

Why?

Metadata enables future capabilities such as

- Source citations
- Metadata filtering
- Document filtering
- Page references

---

# Data Flow

                PDF

                 │

                 ▼

             Page Objects

                 │

                 ▼

            Chunk Objects

                 │

                 ▼

             Embeddings

                 │

                 ▼

     Chunk + Embedding + Metadata

                 │

                 ▼

              ChromaDB

---

# Classes Involved

| Class                    | Responsibility                 |
|--------------------------|---------------------------     |
| IngestionService         | Coordinates ingestion          |
| PDFReader                | Reads PDF pages                |
| TextChunker              | Creates chunks                 |
| EmbeddingService         | Generates embeddings           |
| VectorRepository         | Stores vectors in ChromaDB     |

---

# Design Principles

The ingestion pipeline follows several important principles.

## Orchestration

Only IngestionService controls the workflow.

Individual components never call each other directly.

---

## Single Responsibility

Every class performs exactly one task.

Examples

PDFReader

Reads PDFs only.

TextChunker

Creates chunks only.

EmbeddingService

Generates embeddings only.

VectorRepository

Stores vectors only.

---

## Loose Coupling

The ingestion pipeline does not depend on

- Ollama
- ChromaDB internals
- PDF library internals

These dependencies are isolated behind dedicated services.

---

# Output of the Pipeline

The ingestion pipeline produces a searchable knowledge base.

Each stored record contains

- Document Text
- Vector Embedding
- Document Metadata

This knowledge base becomes the input for the Retrieval Pipeline.