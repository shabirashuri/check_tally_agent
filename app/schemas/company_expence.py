from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CompanyExpenseBase(BaseModel):
    """Base schema for company expenses (cheques)"""
    cheque_number: str = Field(..., description="Cheque number")
    payee_name: str = Field(..., description="Person or company receiving payment")
    amount: float = Field(..., gt=0, description="Cheque amount")
    issue_date: Optional[str] = Field(None, description="Cheque issue date (YYYY-MM-DD)")


class CompanyExpenseCreate(CompanyExpenseBase):
    """Schema for creating company expenses"""
    pass


class CompanyExpenseResponse(CompanyExpenseBase):
    """Schema for company expense response"""
    id: int
    session_id: str
    created_at: datetime
    raw_text: Optional[str] = None

    class Config:
        from_attributes = True
