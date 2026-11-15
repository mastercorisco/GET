"""E02 library and knowledge

Revision ID: 002
Revises: 001
Create Date: 2026-11-15
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "library",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "library_version",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("library_id", sa.String(36), sa.ForeignKey("library.id"), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("library_id", "version", name="uq_library_version"),
    )
    op.create_table(
        "knowledge_item",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("scope_type", sa.String(32), nullable=False),
        sa.Column("scope_id", sa.String(36), nullable=False),
        sa.Column("human_code", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_knowledge_item_scope",
        "knowledge_item",
        ["scope_type", "scope_id"],
    )
    op.create_table(
        "knowledge_item_alias",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("item_id", sa.String(36), sa.ForeignKey("knowledge_item.id"), nullable=False),
        sa.Column("alias", sa.Text(), nullable=False),
        sa.UniqueConstraint("item_id", "alias", name="uq_knowledge_item_alias"),
    )
    op.create_table(
        "knowledge_draft",
        sa.Column("item_id", sa.String(36), sa.ForeignKey("knowledge_item.id"), primary_key=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("content_md", sa.Text(), nullable=False),
        sa.Column("origin_context", sa.Text(), nullable=False),
        sa.Column("knowledge_type", sa.String(64), nullable=False),
        sa.Column("maturity", sa.String(32), nullable=False),
        sa.Column("approval", sa.String(32), nullable=False),
        sa.Column("lifecycle", sa.String(32), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "knowledge_revision",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("item_id", sa.String(36), sa.ForeignKey("knowledge_item.id"), nullable=False),
        sa.Column("revision_num", sa.Integer(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("content_md", sa.Text(), nullable=False),
        sa.Column("origin_context", sa.Text(), nullable=False),
        sa.Column("knowledge_type", sa.String(64), nullable=False),
        sa.Column("maturity", sa.String(32), nullable=False),
        sa.Column("approval", sa.String(32), nullable=False),
        sa.Column("lifecycle", sa.String(32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("item_id", "revision_num", name="uq_knowledge_revision_num"),
    )
    op.create_table(
        "relation_type",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("code", sa.String(64), nullable=False, unique=True),
        sa.Column("label", sa.String(255), nullable=False),
    )
    op.create_table(
        "knowledge_relation",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("relation_type_id", sa.String(36), sa.ForeignKey("relation_type.id"), nullable=False),
        sa.Column("source_item_id", sa.String(36), sa.ForeignKey("knowledge_item.id"), nullable=False),
        sa.Column("target_item_id", sa.String(36), sa.ForeignKey("knowledge_item.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "source_item_id != target_item_id",
            name="ck_knowledge_relation_no_self",
        ),
    )
    op.execute(
        """
        CREATE VIRTUAL TABLE knowledge_revision_fts USING fts5(
            item_id UNINDEXED,
            kind UNINDEXED,
            title,
            content,
            origin_context,
            tokenize = 'unicode61'
        )
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS knowledge_revision_fts")
    op.drop_table("knowledge_relation")
    op.drop_table("relation_type")
    op.drop_table("knowledge_revision")
    op.drop_table("knowledge_draft")
    op.drop_table("knowledge_item_alias")
    op.drop_index("ix_knowledge_item_scope", table_name="knowledge_item")
    op.drop_table("knowledge_item")
    op.drop_table("library_version")
    op.drop_table("library")
