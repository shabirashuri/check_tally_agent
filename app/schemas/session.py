from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from app.schemas.company_expence import CompanyExpenseResponse
from app.schemas.bank_transactions import BankTransactionResponse


class SessionCreate(BaseModel):
    session_name: str


class SessionResponse(BaseModel):
    id: str
    user_id: str
    session_name: str
    created_at: datetime

    class Config:
        from_attributes = True


class SessionDetailResponse(SessionResponse):
    """Detailed session response with related data"""
    company_expenses: List[CompanyExpenseResponse] = []
    bank_transactions: List[BankTransactionResponse] = []

    class Config:
        from_attributes = True