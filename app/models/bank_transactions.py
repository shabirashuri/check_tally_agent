from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


# ---------------- BANK TRANSACTIONS ----------------
class BankTransaction(Base):
    __tablename__ = "bank_transactions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("sessions.id", ondelete="CASCADE"))

    cheque_number = Column(String, index=True)
    amount = Column(Float)
    clearing_date = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    raw_text = Column(Text)

    session = relationship("Session", back_populates="bank_transactions")

