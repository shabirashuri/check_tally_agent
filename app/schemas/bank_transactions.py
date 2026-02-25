from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class BankTransactionBase(BaseModel):
    """Base schema for bank transactions"""
    cheque_number: str = Field(..., description="Cheque number")
    amount: float = Field(..., gt=0, description="Cleared amount")
    clearing_date: str = Field(..., description="Date cheque was cleared (YYYY-MM-DD)")


class BankTransactionCreate(BankTransactionBase):
    """Schema for creating bank transactions"""
    pass


class BankTransactionResponse(BankTransactionBase):
    """Schema for bank transaction response"""
    id: int
    session_id: str
    created_at: datetime
    raw_text: Optional[str] = None
    
    class Config:
        from_attributes = True
