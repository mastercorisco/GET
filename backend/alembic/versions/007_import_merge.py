"""E07 import staging merge and change proposals

Revision ID: 007
Revises: 006
Create Date: 2026-11-15
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "007"
down_revision: Union[str, None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "import_record",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("project_id", sa.String(36), sa.ForeignKey("project.id"), nullable=False),
        sa.Column("source_filename", sa.String(512), nullable=False),
        sa.Column("raw_path", sa.Text(), nullable=False),
        sa.Column("package_type", sa.String(32), nullable=False),
        sa.Column("schema_name", sa.String(64), nullable=False),
        sa.Column("schema_version", sa.String(32), nullable=False),
        sa.Column("linked_export_id", sa.String(64), nullable=True),
        sa.Column("export_record_id", sa.String(36), sa.ForeignKey("export_record.id"), nullable=True),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_import_record_project", "import_record", ["project_id"])

    op.create_table(
        "import_staging_item",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("import_id", sa.String(36), sa.ForeignKey("import_record.id"), nullable=False),
        sa.Column("entity_kind", sa.String(32), nullable=False),
        sa.Column("entity_key", sa.String(128), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=False),
    )
    op.create_index("ix_import_staging_import", "import_staging_item", ["import_id"])

    op.create_table(
        "import_quarantine_item",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("import_id", sa.String(36), sa.ForeignKey("import_record.id"), nullable=False),
        sa.Column("path", sa.String(256), nullable=False),
        sa.Column("error_code", sa.String(64), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=True),
    )
    op.create_index("ix_import_quarantine_import", "import_quarantine_item", ["import_id"])

    op.create_table(
        "merge_session",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("import_id", sa.String(36), sa.ForeignKey("import_record.id"), nullable=False),
        sa.Column("project_id", sa.String(36), sa.ForeignKey("project.id"), nullable=False),
        sa.Column("base_export_id", sa.String(64), nullable=False),
        sa.Column("baseline_id", sa.String(36), sa.ForeignKey("baseline.id"), nullable=False),
        sa.Column("fascicle_node_id", sa.String(36), sa.ForeignKey("document_node.id"), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("summary_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_merge_session_import", "merge_session", ["import_id"])

    op.create_table(
        "change_proposal",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("merge_session_id", sa.String(36), sa.ForeignKey("merge_session.id"), nullable=False),
        sa.Column("proposal_kind", sa.String(32), nullable=False),
        sa.Column("target_item_id", sa.String(128), nullable=False),
        sa.Column("title", sa.String(512), nullable=False),
        sa.Column("field_changes_json", sa.Text(), nullable=False),
        sa.Column("conflict", sa.Boolean(), nullable=False),
        sa.Column("protected_touch", sa.Boolean(), nullable=False),
    )
    op.create_index("ix_change_proposal_session", "change_proposal", ["merge_session_id"])
    op.create_index("ix_change_proposal_target", "change_proposal", ["target_item_id"])

    op.create_table(
        "change_decision",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("proposal_id", sa.String(36), sa.ForeignKey("change_proposal.id"), nullable=False, unique=True),
        sa.Column("decision", sa.String(32), nullable=True),
        sa.Column("destination", sa.String(32), nullable=True),
        sa.Column("confirmed_protected", sa.Boolean(), nullable=False),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("change_decision")
    op.drop_table("change_proposal")
    op.drop_table("merge_session")
    op.drop_table("import_quarantine_item")
    op.drop_table("import_staging_item")
    op.drop_table("import_record")