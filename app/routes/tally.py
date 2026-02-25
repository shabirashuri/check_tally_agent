"""
Tally/Reconciliation Routes - Endpoints for cheque reconciliation
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.schemas.cheque import TallyReportResponse
from app.utils.jwt_handler import get_current_user
from app.services.tally import run_tally_reconciliation, get_tally_report


router = APIRouter(prefix="/sessions/{session_id}/tally", tags=["tally"])


@router.post("/run", response_model=TallyReportResponse)
def run_tally(
    session_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Run cheque reconciliation and generate tally report
    
    Compares company expenses with bank transactions to identify:
    - Cashed cheques
    - Uncashed/pending cheques
    
    Args:
        session_id: Session ID
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Tally report with cashed and uncashed cheques
    """
    user_id = current_user.get("sub")
    return run_tally_reconciliation(session_id, user_id, db)


@router.get("/report", response_model=TallyReportResponse)
def get_report(
    session_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get stored tally report for a session
    
    Args:
        session_id: Session ID
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Stored tally report
    """
    user_id = current_user.get("sub")
    return get_tally_report(session_id, user_id, db)
