from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


# ---------------- COMPANY EXPENSE ----------------
class CompanyExpense(Base):
    __tablename__ = "company_expenses"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("sessions.id", ondelete="CASCADE"))

    cheque_number = Column(String, index=True)
    payee_name = Column(String)
    amount = Column(Float)
    issue_date = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    raw_text = Column(Text)  # optional: store extracted text

    session = relationship("Session", back_populates="company_expenses")

