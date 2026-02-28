"""Add cascade deletes to sessions relationships

Revision ID: 88fa39c965d1
Revises: 
Create Date: 2026-02-27 21:50:02.751303

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '88fa39c965d1'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop existing foreign key constraints
    op.drop_constraint('company_expenses_session_id_fkey', 'company_expenses', type_='foreignkey')
    op.drop_constraint('bank_transactions_session_id_fkey', 'bank_transactions', type_='foreignkey')
    op.drop_constraint('tally_results_session_id_fkey', 'tally_results', type_='foreignkey')
    
    # Recreate foreign key constraints with ON DELETE CASCADE
    op.create_foreign_key(
        'company_expenses_session_id_fkey',
        'company_expenses',
        'sessions',
        ['session_id'],
        ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'bank_transactions_session_id_fkey',
        'bank_transactions',
        'sessions',
        ['session_id'],
        ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'tally_results_session_id_fkey',
        'tally_results',
        'sessions',
        ['session_id'],
        ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    # Drop the cascading constraints
    op.drop_constraint('company_expenses_session_id_fkey', 'company_expenses', type_='foreignkey')
    op.drop_constraint('bank_transactions_session_id_fkey', 'bank_transactions', type_='foreignkey')
    op.drop_constraint('tally_results_session_id_fkey', 'tally_results', type_='foreignkey')
    
    # Recreate foreign key constraints without ON DELETE CASCADE
    op.create_foreign_key(
        'company_expenses_session_id_fkey',
        'company_expenses',
        'sessions',
        ['session_id'],
        ['id']
    )
    op.create_foreign_key(
        'bank_transactions_session_id_fkey',
        'bank_transactions',
        'sessions',
        ['session_id'],
        ['id']
    )
    op.create_foreign_key(
        'tally_results_session_id_fkey',
        'tally_results',
        'sessions',
        ['session_id'],
        ['id']
    )
