"""
Cheque Reconciliation Business Logic
Compares company-issued cheques with bank-cleared cheques
"""

from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from app.schemas.bank_transactions import BankTransactionResponse
from app.schemas.company_expence import CompanyExpenseResponse
from app.schemas.cheque import CashedCheque, UncashedCheque, TallyReportResponse
from sqlalchemy.orm import Session
from app.models.company_expence import CompanyExpense
from app.models.bank_transactions import BankTransaction
from app.models.tally_results import TallyResult
import json
from datetime import date


def parse_date(date_str: Optional[str]) -> date:
    """
    Parse date string in various formats
    
    Args:
        date_str: Date string (YYYY-MM-DD format preferred), can be None
        
    Returns:
        parsed date object (today's date if None or parsing fails)
    """
    if not date_str:
        return datetime.now().date()
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        try:
            return datetime.strptime(date_str, "%d-%m-%Y").date()
        except ValueError:
            try:
                return datetime.strptime(date_str, "%d/%m/%Y").date()
            except ValueError:
                # Return today's date if parsing fails
                return datetime.now().date()


def reconcile_cheques(
    company_expenses: List[CompanyExpense],
    bank_transactions: List[BankTransaction]
) -> Tuple[List[CashedCheque], List[UncashedCheque], Dict]:
    """
    Reconcile company cheques with bank-cleared cheques
    
    Args:
        company_expenses: List of company-issued cheques
        bank_transactions: List of bank-cleared cheques
        
    Returns:
        Tuple containing:
        - List of cashed cheques
        - List of uncashed cheques
        - Dictionary with unmatched information
    """
    
    cashed_cheques: List[CashedCheque] = []
    uncashed_cheques: List[UncashedCheque] = []
    unmatched_bank = set()
    unmatched_company = set()
    
    # Create lookup dictionaries for faster matching
    bank_cheques_by_number: Dict[str, BankTransaction] = {}
    for bt in bank_transactions:
        bank_cheques_by_number[bt.cheque_number.strip().upper()] = bt
    
    unmatched_bank = set(bank_cheques_by_number.keys())
    
    # Process each company cheque
    for company_expense in company_expenses:
        cheque_key = company_expense.cheque_number.strip().upper()
        
        # Look for matching bank transaction
        if cheque_key in bank_cheques_by_number:
            bank_txn = bank_cheques_by_number[cheque_key]
            
            # Verify amount matches (allow small differences for rounding)
            if abs(company_expense.amount - bank_txn.amount) < 0.01:
                # Cheque has been cashed
                cashed_cheques.append(
                    CashedCheque(
                        company_cheque_number=company_expense.cheque_number,
                        bank_cheque_number=bank_txn.cheque_number,
                        payee_name=company_expense.payee_name,
                        amount=company_expense.amount,
                        issue_date=company_expense.issue_date or None,  # Handle None gracefully
                        clearing_date=bank_txn.clearing_date
                    )
                )
                unmatched_bank.discard(cheque_key)
            else:
                # Amount mismatch - treat as uncashed
                uncashed_cheques.append(
                    UncashedCheque(
                        cheque_number=company_expense.cheque_number,
                        payee_name=company_expense.payee_name,
                        amount=company_expense.amount,
                        issue_date=company_expense.issue_date or None,  # Handle None gracefully
                        days_outstanding=calculate_days_outstanding(company_expense.issue_date)
                    )
                )
                unmatched_company.add(cheque_key)
        else:
            # No matching bank transaction - cheque is uncashed
            uncashed_cheques.append(
                UncashedCheque(
                    cheque_number=company_expense.cheque_number,
                    payee_name=company_expense.payee_name,
                    amount=company_expense.amount,
                    issue_date=company_expense.issue_date or None,  # Handle None gracefully
                    days_outstanding=calculate_days_outstanding(company_expense.issue_date)
                )
            )
            unmatched_company.add(cheque_key)
    
    # Create unmatched info
    unmatched_info = {
        "unmatched_bank_cheques": list(unmatched_bank),
        "unmatched_company_cheques": list(unmatched_company),
        "bank_cheques_without_company_record": len(unmatched_bank),
        "company_cheques_without_bank_clearance": len(unmatched_company)
    }
    
    return cashed_cheques, uncashed_cheques, unmatched_info


def calculate_days_outstanding(issue_date_str: Optional[str]) -> int:
    """
    Calculate days outstanding for a cheque
    
    Args:
        issue_date_str: Issue date as string (can be None)
        
    Returns:
        Number of days since issue (0 if date is None or invalid)
    """
    if not issue_date_str:
        return 0
    try:
        issue_date = parse_date(issue_date_str)
        today = datetime.now().date()
        delta = today - issue_date
        return max(0, delta.days)
    except Exception:
        return 0


def calculate_totals(
    cashed_cheques: List[CashedCheque],
    uncashed_cheques: List[UncashedCheque]
) -> Tuple[float, float]:
    """
    Calculate total amounts for cashed and uncashed cheques
    
    Args:
        cashed_cheques: List of cashed cheques
        uncashed_cheques: List of uncashed cheques
        
    Returns:
        Tuple of (total_cashed_amount, total_uncashed_amount)
    """
    total_cashed = sum(cheque.amount for cheque in cashed_cheques)
    total_uncashed = sum(cheque.amount for cheque in uncashed_cheques)
    
    return total_cashed, total_uncashed


def generate_tally_report(
    session_id: str,
    cashed_cheques: List[CashedCheque],
    uncashed_cheques: List[UncashedCheque]
) -> TallyReportResponse:
    """
    Generate final tally report
    
    Args:
        session_id: Session ID
        cashed_cheques: List of cashed cheques
        uncashed_cheques: List of uncashed cheques
        
    Returns:
        TallyReportResponse with complete report
    """
    total_cashed, total_uncashed = calculate_totals(cashed_cheques, uncashed_cheques)
    
    return TallyReportResponse(
        session_id=session_id,
        total_cashed_cheques=len(cashed_cheques),
        total_uncashed_cheques=len(uncashed_cheques),
        total_cashed_amount=total_cashed,
        total_uncashed_amount=total_uncashed,
        cashed_cheques=cashed_cheques,
        uncashed_cheques=uncashed_cheques,
        created_at=datetime.utcnow()
    )


def store_tally_result(
    db: Session,
    session_id: str,
    cashed_cheques: List[CashedCheque],
    uncashed_cheques: List[UncashedCheque],
    unmatched_info: Dict
) -> TallyResult:
    """
    Store tally results in database
    
    Args:
        db: Database session
        session_id: Session ID
        cashed_cheques: List of cashed cheques
        uncashed_cheques: List of uncashed cheques
        unmatched_info: Unmatched information
        
    Returns:
        Created TallyResult object
    """
    total_cashed, total_uncashed = calculate_totals(cashed_cheques, uncashed_cheques)
    
    # Check if tally already exists for this session
    existing_tally = db.query(TallyResult).filter(
        TallyResult.session_id == session_id
    ).first()
    
    if existing_tally:
        # Update existing tally
        existing_tally.cashed = json.dumps([c.dict() for c in cashed_cheques])
        existing_tally.pending = json.dumps([u.dict() for u in uncashed_cheques])
        existing_tally.unmatched = json.dumps(unmatched_info)
        existing_tally.total_cashed_amount = total_cashed
        existing_tally.total_pending_amount = total_uncashed
        db.commit()
        return existing_tally
    else:
        # Create new tally
        tally = TallyResult(
            session_id=session_id,
            cashed=json.dumps([c.dict() for c in cashed_cheques]),
            pending=json.dumps([u.dict() for u in uncashed_cheques]),
            unmatched=json.dumps(unmatched_info),
            total_cashed_amount=total_cashed,
            total_pending_amount=total_uncashed
        )
        db.add(tally)
        db.commit()
        db.refresh(tally)
        return tally
