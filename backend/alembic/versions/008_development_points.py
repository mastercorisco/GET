"""E08 development points and block metadata

Revision ID: 008
Revises: 007
Create Date: 2026-11-15
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "008"
down_revision: Union[str, None] = "007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("document_node", sa.Column("objective", sa.Text(), nullable=False, server_default=""))
    op.add_column("document_node", sa.Column("scope", sa.Text(), nullable=False, server_default=""))
    op.add_column(
        "document_node",
        sa.Column("target_output_json", sa.Text(), nullable=False, server_default='{}'),
    )
    op.add_column(
        "document_node",
        sa.Column("block_status", sa.String(32), nullable=False, server_default="active"),
    )

    op.add_column(
        "workspace_settings",
        sa.Column("help_level", sa.String(16), nullable=False, server_default="normal"),
    )

    op.create_table(
        "premise",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("owner_kind", sa.String(32), nullable=False),
        sa.Column("owner_id", sa.String(36), nullable=False),
        sa.Column("statement", sa.Text(), nullable=False),
        sa.Column("importance", sa.String(32), nullable=False),
        sa.Column("source_type", sa.String(64), nullable=False),
        sa.Column("confidence", sa.String(32), nullable=False),
        sa.Column("reference_id", sa.String(36), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_premise_owner", "premise", ["owner_kind", "owner_id"])

    op.create_table(
        "development_point",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "block_id",
            sa.String(36),
            sa.ForeignKey("document_node.id"),
            nullable=False,
        ),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(255), nullable=False, server_default=""),
        sa.Column("core_idea", sa.Text(), nullable=False, server_default=""),
        sa.Column("intended_outcome", sa.Text(), nullable=False, server_default=""),
        sa.Column("llm_freedom", sa.String(32), nullable=False, server_default="strict"),
        sa.Column("status", sa.String(32), nullable=False, server_default="draft"),
        sa.Column("template_id", sa.String(64), nullable=True),
        sa.Column("needs_review", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("lists_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("block_id", "sort_order", name="uq_development_point_block_order"),
    )


def downgrade() -> None:
    op.drop_table("development_point")
    op.drop_index("ix_premise_owner", table_name="premise")
    op.drop_table("premise")
    op.drop_column("workspace_settings", "help_level")
    op.drop_column("document_node", "block_status")
    op.drop_column("document_node", "target_output_json")
    op.drop_column("document_node", "scope")
    op.drop_column("document_node", "objective")