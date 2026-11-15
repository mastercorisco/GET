"""E03 projects and technical structure

Revision ID: 003
Revises: 002
Create Date: 2026-11-15
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "project_template",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("code", sa.String(64), nullable=False, unique=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "project_template_version",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "template_id",
            sa.String(36),
            sa.ForeignKey("project_template.id"),
            nullable=False,
        ),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("metadata_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("template_id", "version", name="uq_project_template_version"),
    )
    op.create_table(
        "project",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column(
            "template_version_id",
            sa.String(36),
            sa.ForeignKey("project_template_version.id"),
            nullable=False,
        ),
        sa.Column("intervention_type", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "project_library_pin",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("project_id", sa.String(36), sa.ForeignKey("project.id"), nullable=False, unique=True),
        sa.Column(
            "library_version_id",
            sa.String(36),
            sa.ForeignKey("library_version.id"),
            nullable=False,
        ),
        sa.Column("pinned_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "technical_class",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("kind", sa.String(32), nullable=False),
        sa.Column("code", sa.String(64), nullable=False),
        sa.Column("label", sa.String(255), nullable=False),
        sa.UniqueConstraint("kind", "code", name="uq_technical_class_kind_code"),
    )
    op.create_table(
        "technical_instance",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("project_id", sa.String(36), sa.ForeignKey("project.id"), nullable=False),
        sa.Column(
            "parent_id",
            sa.String(36),
            sa.ForeignKey("technical_instance.id"),
            nullable=True,
        ),
        sa.Column(
            "class_id",
            sa.String(36),
            sa.ForeignKey("technical_class.id"),
            nullable=True,
        ),
        sa.Column("kind", sa.String(32), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("export_code", sa.String(128), nullable=True),
        sa.Column("location_note", sa.Text(), nullable=True),
        sa.Column("reference_note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_technical_instance_project",
        "technical_instance",
        ["project_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_technical_instance_project", table_name="technical_instance")
    op.drop_table("technical_instance")
    op.drop_table("technical_class")
    op.drop_table("project_library_pin")
    op.drop_table("project")
    op.drop_table("project_template_version")
    op.drop_table("project_template")