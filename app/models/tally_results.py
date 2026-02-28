from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


# ---------------- TALLY RESULT ----------------
class TallyResult(Base):
    __tablename__ = "tally_results"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("sessions.id", ondelete="CASCADE"), unique=True)

    cashed = Column(Text)       # JSON string
    pending = Column(Text)     # JSON string
    unmatched = Column(Text)
    total_cashed_amount = Column(Float)
    total_pending_amount = Column(Float)

    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="tally")