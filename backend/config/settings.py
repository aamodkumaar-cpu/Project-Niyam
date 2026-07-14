"""
Project-wide configuration.
Centralizes all configurable values such as model names, database paths and application settings.
This avoids hardcoding values throughout the codebase.
"""

from pathlib import Path
from dotenv import load_dotenv
import os

# --------------------------------------------------------------------
# Project Root
# --------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Load environment variables
load_dotenv(PROJECT_ROOT / ".env")

# --------------------------------------------------------------------
# Directories
# --------------------------------------------------------------------
BACKEND_ROOT = PROJECT_ROOT / "backend"

DATA_DIR = BACKEND_ROOT / "data"

CHROMA_DB_PATH = DATA_DIR / "chroma"

UPLOADS_DIR = DATA_DIR / "uploads"

DOCUMENTS_DIR = BACKEND_ROOT / "documents"

# --------------------------------------------------------------------
# Ollama
# --------------------------------------------------------------------
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")

# --------------------------------------------------------------------
# Vector Database
# --------------------------------------------------------------------
VECTOR_COLLECTION = os.getenv("VECTOR_COLLECTION", "knowledge_base")

# --------------------------------------------------------------------
# Retrieval
# --------------------------------------------------------------------
TOP_K = int(os.getenv("TOP_K", "5"))

# --------------------------------------------------------------------
# Chunking
# --------------------------------------------------------------------
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

# --------------------------------------------------------------------
# Code Flags
# --------------------------------------------------------------------
DEBUG = True