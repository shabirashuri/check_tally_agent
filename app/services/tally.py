"""
Tally Service - Business logic for reconciliation and tally operations
"""

import json
from sqlalchemy.orm import Session
from app.models.session import Session as SessionModel
from app.models.company_expence import CompanyExpense
from app.models.bank_transactions import BankTransaction
from app.models.tally_results import TallyResult
from app.schemas.cheque import TallyReportResponse, CashedCheque, UncashedCheque
from app.services.reconciliation import (
    reconcile_cheques,
    generate_tally_report,
    store_tally_result
)
from fastapi import HTTPException, status


def run_tally_reconciliation(
    session_id: str,
    user_id: str,
    db: Session
) -> TallyReportResponse:
    """
    Execute cheque reconciliation and generate tally report
    
    Args:
        session_id: Session ID
        user_id: User ID for ownership verification
        db: Database session
        
    Returns:
        Tally report with cashed and uncashed cheques
    """
    try:
        # Verify session ownership
        session_obj = db.query(SessionModel).filter(
            SessionModel.id == session_id,
            SessionModel.user_id == user_id
        ).first()
        
        if not session_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Get all company expenses and bank transactions for this session
        company_expenses = db.query(CompanyExpense).filter(
            CompanyExpense.session_id == session_id
        ).all()
        
        bank_transactions = db.query(BankTransaction).filter(
            BankTransaction.session_id == session_id
        ).all()
        
        if not company_expenses or not bank_transactions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session must have both company expenses and bank transactions before running tally"
            )
        
        # Run reconciliation
        cashed_cheques, uncashed_cheques, unmatched_info = reconcile_cheques(
            company_expenses,
            bank_transactions
        )
        
        # Store tally result
        store_tally_result(
            db,
            session_id,
            cashed_cheques,
            uncashed_cheques,
            unmatched_info
        )
        
        # Generate report
        report = generate_tally_report(
            session_id,
            cashed_cheques,
            uncashed_cheques
        )
        
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run tally: {str(e)}"
        )


def get_tally_report(
    session_id: str,
    user_id: str,
    db: Session
) -> TallyReportResponse:
    """
    Retrieve stored tally report for a session
    
    Args:
        session_id: Session ID
        user_id: User ID for ownership verification
        db: Database session
        
    Returns:
        Stored tally report
    """
    try:
        # Verify session ownership
        session_obj = db.query(SessionModel).filter(
            SessionModel.id == session_id,
            SessionModel.user_id == user_id
        ).first()
        
        if not session_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Get tally result
        tally_result = db.query(TallyResult).filter(
            TallyResult.session_id == session_id
        ).first()
        
        if not tally_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tally report not found. Run tally first."
            )
        
        # Parse JSON data
        cashed_data = json.loads(tally_result.cashed) if tally_result.cashed else []
        pending_data = json.loads(tally_result.pending) if tally_result.pending else []
        
        cashed_cheques = [CashedCheque(**c) for c in cashed_data]
        uncashed_cheques = [UncashedCheque(**u) for u in pending_data]
        
        return TallyReportResponse(
            session_id=session_id,
            total_cashed_cheques=len(cashed_cheques),
            total_uncashed_cheques=len(uncashed_cheques),
            total_cashed_amount=tally_result.total_cashed_amount or 0.0,
            total_uncashed_amount=tally_result.total_pending_amount or 0.0,
            cashed_cheques=cashed_cheques,
            uncashed_cheques=uncashed_cheques,
            created_at=tally_result.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve tally report: {str(e)}"
        )
