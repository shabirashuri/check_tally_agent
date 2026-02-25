# This file exists solely to import all models so that
# Base.metadata is fully populated when Alembic reads env.py.
# Import this module in alembic/env.py before using target_metadata.

from app.models.user import User            # noqa: F401
from app.models.session import Session      # noqa: F401
from app.models.bank_transactions import BankTransaction  # noqa: F401
from app.models.company_expence import CompanyExpense     # noqa: F401
from app.models.tally_results import TallyResult          # noqa: F401
