from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ==================== COMPANY CHEQUE SCHEMAS ====================

class CompanyChequeBase(BaseModel):
    """Base schema for company-issued cheques"""
    cheque_number: str = Field(..., description="Cheque number")
    payee_name: str = Field(..., description="Person or company receiving payment")
    amount: float = Field(..., gt=0, description="Cheque amount")
    issue_date: str = Field(..., description="Cheque issue date (YYYY-MM-DD)")


class CompanyChequeCreate(CompanyChequeBase):
    """Schema for creating company cheques"""
    pass


class CompanyChequeResponse(CompanyChequeBase):
    """Schema for company cheque response"""
    id: int
    session_id: str
    created_at: datetime
    raw_text: Optional[str] = None
    
    class Config:
        from_attributes = True


# ==================== BANK CHEQUE SCHEMAS ====================

class BankChequeBase(BaseModel):
    """Base schema for bank-cleared cheques"""
    cheque_number: str = Field(..., description="Cheque number")
    amount: float = Field(..., gt=0, description="Cleared amount")
    clearing_date: str = Field(..., description="Date cheque was cleared (YYYY-MM-DD)")


class BankChequeCreate(BankChequeBase):
    """Schema for creating bank cheques"""
    pass


class BankChequeResponse(BankChequeBase):
    """Schema for bank cheque response"""
    id: int
    session_id: str
    created_at: datetime
    raw_text: Optional[str] = None
    
    class Config:
        from_attributes = True


# ==================== SESSION SCHEMAS ====================

class SessionCreate(BaseModel):
    """Schema for creating a new session"""
    session_name: str = Field(..., min_length=1, description="Name for the reconciliation session")


class SessionResponse(BaseModel):
    """Schema for session response"""
    id: str
    user_id: str
    session_name: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class SessionDetailResponse(SessionResponse):
    """Detailed session response with related data"""
    company_expenses: list[CompanyChequeResponse] = []
    bank_transactions: list[BankChequeResponse] = []


# ==================== TALLY REPORT SCHEMAS ====================

class CashedCheque(BaseModel):
    """Schema for a cashed cheque"""
    company_cheque_number: str
    bank_cheque_number: str
    payee_name: str
    amount: float
    issue_date: str
    clearing_date: str


class UncashedCheque(BaseModel):
    """Schema for an uncashed cheque"""
    cheque_number: str
    payee_name: str
    amount: float
    issue_date: str
    days_outstanding: int


class TallyReportResponse(BaseModel):
    """Final tally report response"""
    session_id: str
    total_cashed_cheques: int
    total_uncashed_cheques: int
    total_cashed_amount: float
    total_uncashed_amount: float
    cashed_cheques: list[CashedCheque]
    uncashed_cheques: list[UncashedCheque]
    created_at: datetime
    
    class Config:
        from_attributes = True
