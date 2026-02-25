"""
Bank Transaction Service - Business logic for bank transaction operations
"""

from sqlalchemy.orm import Session
from app.models.bank_transactions import BankTransaction
from app.models.session import Session as SessionModel
from app.schemas.bank_transactions import BankTransactionResponse
from app.services.llm import extract_bank_cheques
from fastapi import HTTPException, status


def process_bank_transactions(
    session_id: str,
    user_id: str,
    file_content: str,
    db: Session
) -> dict:
    """
    Process and store bank transaction (cleared cheque) data from uploaded file
    
    Args:
        session_id: Session ID
        user_id: User ID for ownership verification
        file_content: Raw text file content
        db: Database session
        
    Returns:
        Dictionary with extraction results and stored transactions
    """
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
    
    try:
        # Extract cheques using LLM
        extraction_result = extract_bank_cheques(file_content)
        
        stored_transactions = []
        
        # Store extracted cheques in database
        for cheque in extraction_result["cheques"]:
            bank_transaction = BankTransaction(
                session_id=session_id,
                cheque_number=cheque["cheque_number"],
                amount=cheque["amount"],
                clearing_date=cheque["clearing_date"],
                raw_text=file_content
            )
            db.add(bank_transaction)
            db.flush()
            
            stored_transactions.append(
                BankTransactionResponse(
                    id=bank_transaction.id,
                    session_id=bank_transaction.session_id,
                    cheque_number=bank_transaction.cheque_number,
                    amount=bank_transaction.amount,
                    clearing_date=bank_transaction.clearing_date,
                    created_at=bank_transaction.created_at
                )
            )
        
        db.commit()
        
        return {
            "status": "success",
            "cheques_extracted": len(stored_transactions),
            "cheques": stored_transactions,
            "extraction_notes": extraction_result["extraction_notes"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process bank transactions: {str(e)}"
        )
