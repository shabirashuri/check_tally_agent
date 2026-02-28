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


def extract_company_cheques(raw_text: str) -> CompanyChequeExtractionResult:
    """
    Extract structured company cheque data from raw text using LLM
    
    Args:
        raw_text: Raw text containing company cheque information
        
    Returns:
        CompanyChequeExtractionResult with extracted cheques
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
    
    result = chain.invoke({"text": raw_text})
    return result


def extract_bank_cheques(raw_text: str) -> BankChequeExtractionResult:
    """
    Extract structured bank cheque data from raw text using LLM
    
    Args:
        raw_text: Raw text containing bank transaction information
        
    Returns:
        BankChequeExtractionResult with extracted cheques
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
    
    result = chain.invoke({"text": raw_text})
    return result

