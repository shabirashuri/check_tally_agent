"""Initial schema

Revision ID: 850d1fbb6b85
Revises: 1a65908c93b3
Create Date: 2026-02-25 14:05:47.159077

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '850d1fbb6b85'
down_revision: Union[str, None] = '1a65908c93b3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
