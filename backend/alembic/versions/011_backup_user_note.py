"""backup_record user_note

Revision ID: 011
Revises: 010
Create Date: 2026-11-22
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "011"
down_revision: Union[str, None] = "010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("backup_record", sa.Column("user_note", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("backup_record", "user_note")