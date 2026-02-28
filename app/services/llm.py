import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from typing import Optional


load_dotenv()

# Removed GROQ-specific code

# ---------------------------------------------------------------------------
# Text chunking
# ---------------------------------------------------------------------------

def chunk_text(text: str, chunk_size: int = 4000) -> list:
    """
    Split raw text into chunks of at most `chunk_size` characters.
    Always breaks at a newline boundary so individual records are never
    split mid-line.

    Args:
        text: Full raw text extracted from a PDF/TXT file.
        chunk_size: Maximum characters per chunk (default 4 000 ≈ ~1 000 tokens).

    Returns:
        List of text chunks.
    """
    lines = text.splitlines(keepends=True)
    chunks: list = []
    current = ""
    for line in lines:
        if len(current) + len(line) > chunk_size and current:
            chunks.append(current)
            current = ""
        current += line
    if current:
        chunks.append(current)
    # Guard: always return at least one chunk
    return chunks if chunks else [text]


def get_llm():
    """Initialize and return ChatOpenAI LLM instance"""
    return ChatOpenAI(model="gpt-4", temperature=0.7)  # Adjusted temperature for OpenAI


# Pydantic models for structured output
class ExtractedCompanyCheque(BaseModel):
    """Extracted company cheque data"""
    cheque_number: str = Field(..., description="The cheque number")
    payee_name: str = Field(..., description="Name of payee/recipient")
    amount: float = Field(..., description="Amount of the cheque")
    issue_date: str = Field(..., description="Date cheque was issued (YYYY-MM-DD)")


class ExtractedBankCheque(BaseModel):
    """Extracted bank cheque data"""
    cheque_number: str = Field(..., description="The cheque number")
    amount: float = Field(..., description="Cleared amount")
    clearing_date: str = Field(..., description="Date cheque was cleared (YYYY-MM-DD)")


class CompanyChequeExtractionResult(BaseModel):
    """Result of company cheque extraction"""
    cheques: list[ExtractedCompanyCheque]
    extraction_notes: str = ""


class BankChequeExtractionResult(BaseModel):
    """Result of bank cheque extraction"""
    cheques: list[ExtractedBankCheque]
    extraction_notes: str = ""


def extract_company_cheques(raw_text: str) -> dict:
    """
    Extract structured company cheque data from raw text using LLM.

    Large inputs are automatically split into chunks of ~4 000 characters
    each. Every chunk is processed in a separate LLM call and the results
    are merged before returning.

    Args:
        raw_text: Raw text containing company cheque information.

    Returns:
        Dict with keys ``cheques`` (list) and ``extraction_notes`` (str).
    """
    llm = get_llm()

    prompt = PromptTemplate(
        template="""You are an expert accounting data extraction system. Extract all company cheque information from the provided text.
        
For each cheque found, extract:
- Cheque number (numeric or alphanumeric identifier)
- Payee name (recipient of payment)
- Amount (in currency, as a number)
- Issue date (when cheque was issued, format as YYYY-MM-DD)

Text to extract from:
{text}

Return a JSON response with this exact structure:
{{
    "cheques": [
        {{
            "cheque_number": "...",
            "payee_name": "...",
            "amount": 0.0,
            "issue_date": "YYYY-MM-DD"
        }}
    ],
    "extraction_notes": "Any notes about extraction quality or challenges"
}}

Be strict about date formats. If you cannot determine a date precisely, use your best estimate or indicate uncertainty in extraction_notes.""",
        input_variables=["text"]
    )

    parser = JsonOutputParser(pydantic_object=CompanyChequeExtractionResult)
    chain = prompt | llm | parser

    # ── Chunked processing ──────────────────────────────────────────────────
    chunks = chunk_text(raw_text)
    all_cheques: list = []
    all_notes: list = []

    for idx, chunk in enumerate(chunks, start=1):
        try:
            result = chain.invoke({"text": chunk})
            all_cheques.extend(result.get("cheques", []))
            note = result.get("extraction_notes", "")
            if note:
                all_notes.append(f"[chunk {idx}/{len(chunks)}] {note}")
        except Exception as e:
            all_notes.append(f"[chunk {idx}/{len(chunks)}] extraction failed: {e}")

    return {
        "cheques": all_cheques,
        "extraction_notes": (
            f"Processed {len(chunks)} chunk(s). " + " | ".join(all_notes)
            if all_notes
            else f"Processed {len(chunks)} chunk(s)."
        ),
    }


def extract_bank_cheques(raw_text: str) -> dict:
    """
    Extract structured bank cheque data from raw text using LLM.

    Large inputs are automatically split into chunks of ~4 000 characters
    each. Every chunk is processed in a separate LLM call and the results
    are merged before returning.

    Args:
        raw_text: Raw text containing bank transaction information.

    Returns:
        Dict with keys ``cheques`` (list) and ``extraction_notes`` (str).
    """
    llm = get_llm()

    prompt = PromptTemplate(
        template="""You are an expert banking data extraction system. Extract all cleared cheque information from provided bank statements or transaction data.

For each cleared cheque found, extract:
- Cheque number (numeric or alphanumeric identifier)
- Amount (cleared amount in currency, as a number)
- Clearing date (when cheque cleared the bank, format as YYYY-MM-DD)
- if shown instno instead of checque number consider it as checque number
Text to extract from:
{text}

Return a JSON response with this exact structure:
{{
    "cheques": [
        {{
            "cheque_number": "...",
            "amount": 0.0,
            "clearing_date": "YYYY-MM-DD"
        }}
    ],
    "extraction_notes": "Any notes about extraction quality or challenges"
}}

Be strict about date formats. If you cannot determine a date precisely, use your best estimate or indicate uncertainty in extraction_notes.
Only extract CLEARED cheques (cheques that have already been processed by the bank).""",
        input_variables=["text"]
    )

    parser = JsonOutputParser(pydantic_object=BankChequeExtractionResult)
    chain = prompt | llm | parser

    # ── Chunked processing ──────────────────────────────────────────────────
    chunks = chunk_text(raw_text)
    all_cheques: list = []
    all_notes: list = []

    for idx, chunk in enumerate(chunks, start=1):
        try:
            result = chain.invoke({"text": chunk})
            all_cheques.extend(result.get("cheques", []))
            note = result.get("extraction_notes", "")
            if note:
                all_notes.append(f"[chunk {idx}/{len(chunks)}] {note}")
        except Exception as e:
            all_notes.append(f"[chunk {idx}/{len(chunks)}] extraction failed: {e}")

    return {
        "cheques": all_cheques,
        "extraction_notes": (
            f"Processed {len(chunks)} chunk(s). " + " | ".join(all_notes)
            if all_notes
            else f"Processed {len(chunks)} chunk(s)."
        ),
    }

