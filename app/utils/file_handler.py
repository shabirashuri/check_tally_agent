"""
File handling utilities for different file types (TXT, PDF)
"""

import io
from fastapi import HTTPException, status
from PyPDF2 import PdfReader


def extract_text_from_file(file_content: bytes, filename: str) -> str:
    """
    Extract text from either TXT or PDF files
    
    Args:
        file_content: Raw bytes of the uploaded file
        filename: Name of the file (used to determine type)
        
    Returns:
        Extracted text content
        
    Raises:
        HTTPException: If file type not supported or extraction fails
    """
    file_extension = filename.lower().split('.')[-1]
    
    if file_extension == 'txt':
        return extract_text_from_txt(file_content)
    elif file_extension == 'pdf':
        return extract_text_from_pdf(file_content)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format: .{file_extension}. Supported formats: .txt, .pdf"
        )


def extract_text_from_txt(file_content: bytes) -> str:
    """
    Extract text from TXT files
    
    Args:
        file_content: Raw bytes of the text file
        
    Returns:
        Decoded text content
        
    Raises:
        HTTPException: If decoding fails
    """
    try:
        return file_content.decode('utf-8')
    except UnicodeDecodeError:
        # Try alternative encoding
        try:
            return file_content.decode('latin-1')
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to decode text file. Ensure it's encoded in UTF-8 or Latin-1"
            )


def extract_text_from_pdf(file_content: bytes) -> str:
    """
    Extract text from PDF files
    
    Args:
        file_content: Raw bytes of the PDF file
        
    Returns:
        Extracted text from all pages
        
    Raises:
        HTTPException: If PDF extraction fails
    """
    try:
        pdf_file = io.BytesIO(file_content)
        pdf_reader = PdfReader(pdf_file)
        
        if len(pdf_reader.pages) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="PDF file is empty (no pages)"
            )
        
        extracted_text = ""
        for page_num, page in enumerate(pdf_reader.pages):
            page_text = page.extract_text()
            if page_text:
                extracted_text += f"--- PAGE {page_num + 1} ---\n{page_text}\n"
        
        if not extracted_text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="PDF file contains no extractable text (may be scanned image)"
            )
        
        return extracted_text
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to extract text from PDF: {str(e)}"
        )
