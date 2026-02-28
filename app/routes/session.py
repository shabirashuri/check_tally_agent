"""
Session Management Routes - CRUD operations for reconciliation sessions
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.session import Session as SessionModel
from app.schemas.session import SessionCreate, SessionResponse, SessionDetailResponse
from app.schemas.company_expence import CompanyExpenseResponse
from app.schemas.bank_transactions import BankTransactionResponse
from app.utils.jwt_handler import get_current_user
import uuid


router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("/create", response_model=SessionResponse)
def create_session(
    session_data: SessionCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new cheque reconciliation session
    
    Args:
        session_data: Session creation data with name
        current_user: Authenticated user (from JWT)
        db: Database session
        
    Returns:
        Created session details
    """
    try:
        new_session = SessionModel(
            id=str(uuid.uuid4()),
            user_id=current_user.get("sub"),
            session_name=session_data.session_name
        )
        
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        
        return SessionResponse(
            id=new_session.id,
            user_id=new_session.user_id,
            session_name=new_session.session_name,
            created_at=new_session.created_at
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create session: {str(e)}"
        )


@router.get("/", response_model=list[SessionResponse])
def list_sessions(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all sessions for the current user
    
    Args:
        current_user: Authenticated user
        db: Database session
        
    Returns:
        List of user's sessions
    """
    sessions = db.query(SessionModel).filter(
        SessionModel.user_id == current_user.get("sub")
    ).all()
    
    return [
        SessionResponse(
            id=s.id,
            user_id=s.user_id,
            session_name=s.session_name,
            created_at=s.created_at
        )
        for s in sessions
    ]


@router.get("/{session_id}", response_model=SessionDetailResponse)
def get_session(
    session_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get session details with all related data
    
    Args:
        session_id: ID of the session
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Detailed session information
    """
    session_obj = db.query(SessionModel).filter(
        SessionModel.id == session_id,
        SessionModel.user_id == current_user.get("sub")
    ).first()
    
    if not session_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return SessionDetailResponse(
        id=session_obj.id,
        user_id=session_obj.user_id,
        session_name=session_obj.session_name,
        created_at=session_obj.created_at,
        company_expenses=[
            CompanyExpenseResponse(
                id=ce.id,
                session_id=ce.session_id,
                cheque_number=ce.cheque_number,
                payee_name=ce.payee_name,
                amount=ce.amount,
                issue_date=ce.issue_date,
                created_at=ce.created_at,
                raw_text=ce.raw_text
            )
            for ce in session_obj.company_expenses
        ],
        bank_transactions=[
            BankTransactionResponse(
                id=bt.id,
                session_id=bt.session_id,
                cheque_number=bt.cheque_number,
                amount=bt.amount,
                clearing_date=bt.clearing_date,
                created_at=bt.created_at,
                raw_text=bt.raw_text
            )
            for bt in session_obj.bank_transactions
        ]
    )


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_id: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a session by its ID

    Args:
        session_id: ID of the session to delete
        current_user: Authenticated user (from JWT)
        db: Database session

    Returns:
        HTTP 204 No Content on successful deletion
    """
    session = db.query(SessionModel).filter(SessionModel.id == session_id, SessionModel.user_id == current_user.get("sub")).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    db.delete(session)
    db.commit()

    return
