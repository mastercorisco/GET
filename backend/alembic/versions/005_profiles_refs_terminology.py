"""E05 technical profiles, references, terminology

Revision ID: 005
Revises: 004
Create Date: 2026-11-15
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "technical_profile_draft",
        sa.Column("item_id", sa.String(36), sa.ForeignKey("knowledge_item.id"), primary_key=True),
        sa.Column("profile_type", sa.String(32), nullable=False),
        sa.Column("data_json", sa.Text(), nullable=False),
    )
    op.create_table(
        "technical_profile_payload",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "revision_id",
            sa.String(36),
            sa.ForeignKey("knowledge_revision.id"),
            nullable=False,
            unique=True,
        ),
        sa.Column("profile_type", sa.String(32), nullable=False),
        sa.Column("data_json", sa.Text(), nullable=False),
    )
    op.create_table(
        "reference",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("scope_type", sa.String(32), nullable=False),
        sa.Column("scope_id", sa.String(36), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("citation", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_reference_scope", "reference", ["scope_type", "scope_id"])
    op.create_table(
        "standard_profile",
        sa.Column("reference_id", sa.String(36), sa.ForeignKey("reference.id"), primary_key=True),
        sa.Column("code", sa.String(128), nullable=True),
        sa.Column("issuing_body", sa.String(255), nullable=True),
        sa.Column("edition", sa.String(64), nullable=True),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("lifecycle_state", sa.String(64), nullable=True),
        sa.Column("contractual_role", sa.String(64), nullable=True),
        sa.Column("applicability_text", sa.Text(), nullable=True),
        sa.Column("clauses_json", sa.Text(), nullable=True),
        sa.Column("eda_interpretation", sa.Text(), nullable=True),
        sa.Column("evidence_required", sa.Text(), nullable=True),
        sa.Column("verification_state", sa.String(64), nullable=True),
        sa.Column("internal_location", sa.String(255), nullable=True),
    )
    op.create_table(
        "terminology_concept",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("scope_type", sa.String(32), nullable=False),
        sa.Column("scope_id", sa.String(36), nullable=False),
        sa.Column("preferred_term", sa.String(255), nullable=False),
        sa.Column("definition", sa.Text(), nullable=False),
        sa.Column("language", sa.String(16), nullable=False, server_default="pt"),
        sa.Column("acronym", sa.String(64), nullable=True),
        sa.Column("synonyms_json", sa.Text(), nullable=True),
        sa.Column("avoid_terms_json", sa.Text(), nullable=True),
        sa.Column("technical_translation", sa.String(255), nullable=True),
        sa.Column("domain", sa.String(128), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_terminology_scope", "terminology_concept", ["scope_type", "scope_id"])
    op.create_table(
        "project_terminology_override",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("project_id", sa.String(36), sa.ForeignKey("project.id"), nullable=False),
        sa.Column(
            "concept_id",
            sa.String(36),
            sa.ForeignKey("terminology_concept.id"),
            nullable=False,
        ),
        sa.Column("legacy_term", sa.String(255), nullable=True),
        sa.Column("avoid_in_project", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("usage_note", sa.Text(), nullable=True),
        sa.UniqueConstraint("project_id", "concept_id", name="uq_project_terminology_override"),
    )


def downgrade() -> None:
    op.drop_table("project_terminology_override")
    op.drop_index("ix_terminology_scope", table_name="terminology_concept")
    op.drop_table("terminology_concept")
    op.drop_table("standard_profile")
    op.drop_index("ix_reference_scope", table_name="reference")
    op.drop_table("reference")
    op.drop_table("technical_profile_payload")
    op.drop_table("technical_profile_draft")