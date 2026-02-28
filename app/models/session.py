from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.base import Base

# ---------------- SESSIONS ----------------
class Session(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    session_name = Column(String , nullable=False)

    user = relationship("User", back_populates="sessions")

    company_expenses = relationship("CompanyExpense", back_populates="session", cascade="all, delete-orphan")
    bank_transactions = relationship("BankTransaction", back_populates="session", cascade="all, delete-orphan")
    tally = relationship("TallyResult", back_populates="session", uselist=False, cascade="all, delete-orphan")
