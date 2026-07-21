"""
Knowledge Domain.

Purpose:
    Defines the compliance domain for a document.

Responsibilities:
    - Identify the business domain
    - Standardize domain names

Does NOT:
    - Read documents
    - Perform retrieval
    - Store data
"""

from enum import Enum


class KnowledgeDomain(Enum):

    GST = "GST"
    PF = "PF"
    ESIC = "ESIC"
    LABOUR = "LABOUR"
    MCA = "MCA"
    TDS = "TDS"
    INCOME_TAX = "INCOME_TAX"
    MSME = "MSME"
    GENERAL = "GENERAL"