"""E06 baseline and export records

Revision ID: 006
Revises: 005
Create Date: 2026-11-15
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "baseline",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("project_id", sa.String(36), sa.ForeignKey("project.id"), nullable=False),
        sa.Column("code", sa.String(32), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("library_version_id", sa.String(36), sa.ForeignKey("library_version.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("project_id", "revision", name="uq_baseline_project_revision"),
    )
    op.create_table(
        "baseline_entry",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("baseline_id", sa.String(36), sa.ForeignKey("baseline.id"), nullable=False),
        sa.Column("entity_type", sa.String(32), nullable=False),
        sa.Column("entity_id", sa.String(36), nullable=False),
        sa.Column("revision_num", sa.Integer(), nullable=False),
        sa.UniqueConstraint("baseline_id", "entity_id", name="uq_baseline_entry_entity"),
    )
    op.create_table(
        "baseline_document_code",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("baseline_id", sa.String(36), sa.ForeignKey("baseline.id"), nullable=False),
        sa.Column("document_node_id", sa.String(36), sa.ForeignKey("document_node.id"), nullable=False),
        sa.Column("display_code", sa.String(128), nullable=False),
        sa.UniqueConstraint("baseline_id", "document_node_id", name="uq_baseline_document_code"),
    )
    op.create_table(
        "export_record",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("project_id", sa.String(36), sa.ForeignKey("project.id"), nullable=False),
        sa.Column("baseline_id", sa.String(36), sa.ForeignKey("baseline.id"), nullable=False),
        sa.Column("export_id", sa.String(64), nullable=False, unique=True),
        sa.Column("profile", sa.String(32), nullable=False),
        sa.Column("schema_name", sa.String(64), nullable=False),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("file_path", sa.Text(), nullable=False),
        sa.Column("package_type", sa.String(32), nullable=False),
        sa.Column("parent_export_id", sa.String(36), sa.ForeignKey("export_record.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("export_record")
    op.drop_table("baseline_document_code")
    op.drop_table("baseline_entry")
    op.drop_table("baseline")