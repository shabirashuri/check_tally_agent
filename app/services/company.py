"""
Company Expense Service - Business logic for company cheque operations
"""

from sqlalchemy.orm import Session
from app.models.company_expence import CompanyExpense
from app.models.session import Session as SessionModel
from app.schemas.company_expence import CompanyExpenseResponse
from app.services.llm import extract_company_cheques
from fastapi import HTTPException, status


def process_company_expenses(
    session_id: str,
    user_id: str,
    file_content: str,
    db: Session
) -> dict:
    """
    Process and store company expense cheques from uploaded file
    
    Args:
        session_id: Session ID
        user_id: User ID for ownership verification
        file_content: Raw text file content
        db: Database session
        
    Returns:
        Dictionary with extraction results and stored cheques
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
        extraction_result = extract_company_cheques(file_content)
        
        stored_cheques = []
        
        # Store extracted cheques in database
        for cheque in extraction_result["cheques"]:
            company_expense = CompanyExpense(
                session_id=session_id,
                cheque_number=cheque["cheque_number"],
                payee_name=cheque["payee_name"],
                amount=cheque["amount"],
                issue_date=cheque["issue_date"],
                raw_text=file_content
            )
            db.add(company_expense)
            db.flush()
            
            stored_cheques.append(
                CompanyExpenseResponse(
                    id=company_expense.id,
                    session_id=company_expense.session_id,
                    cheque_number=company_expense.cheque_number,
                    payee_name=company_expense.payee_name,
                    amount=company_expense.amount,
                    issue_date=company_expense.issue_date,
                    created_at=company_expense.created_at
                )
            )
        
        db.commit()
        
        return {
            "status": "success",
            "cheques_extracted": len(stored_cheques),
            "cheques": stored_cheques,
            "extraction_notes": extraction_result["extraction_notes"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process company expenses: {str(e)}"
        )
