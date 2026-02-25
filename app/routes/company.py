"""
Company Expense Routes - Endpoints for company cheque operations
"""

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.utils.jwt_handler import get_current_user
from app.utils.file_handler import extract_text_from_file
from app.services.company import process_company_expenses


router = APIRouter(prefix="/sessions/{session_id}/company", tags=["company"])


@router.post("/upload-expenses")
def upload_company_expenses(
    session_id: str,
    file: UploadFile = File(...),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload and process company expense (cheque) data
    
    Uses LLM to extract structured cheque data from raw text
    
    Supported file formats: .txt, .pdf
    
    Args:
        session_id: Session ID
        file: Text or PDF file containing company cheque data
        current_user: Authenticated user
        db: Database session
        
    Returns:
        List of extracted and stored cheques
    """
    # Validate file type
    allowed_extensions = ['txt', 'pdf']
    file_extension = file.filename.lower().split('.')[-1]
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Supported: {', '.join(allowed_extensions)}"
        )
    
    # Read file content
    file_content = file.file.read()
    
    # Extract text from file (handles both TXT and PDF)
    extracted_text = extract_text_from_file(file_content, file.filename)
    
    user_id = current_user.get("sub")
    
    return process_company_expenses(session_id, user_id, extracted_text, db)
