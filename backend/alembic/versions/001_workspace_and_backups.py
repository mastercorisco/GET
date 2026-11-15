"""E01 workspace and backups

Revision ID: 001
Revises:
Create Date: 2026-11-14
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "workspace_settings",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("root_path", sa.Text(), nullable=False, unique=True),
        sa.Column("local_user_name", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("schema_versions_json", sa.Text(), nullable=False),
        sa.Column("retention_critical", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("retention_daily", sa.Integer(), nullable=False, server_default="14"),
        sa.Column("retention_weekly", sa.Integer(), nullable=False, server_default="8"),
    )
    op.create_table(
        "backup_record",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tier", sa.String(32), nullable=False),
        sa.Column("file_path", sa.Text(), nullable=False),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("preview_meta_json", sa.Text(), nullable=False, server_default="{}"),
    )


def downgrade() -> None:
    op.drop_table("backup_record")
    op.drop_table("workspace_settings")