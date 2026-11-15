"""E04 document structure

Revision ID: 004
Revises: 003
Create Date: 2026-11-15
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "association_role",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("code", sa.String(64), nullable=False, unique=True),
        sa.Column("label", sa.String(255), nullable=False),
    )
    op.create_table(
        "document_node",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("project_id", sa.String(36), sa.ForeignKey("project.id"), nullable=False),
        sa.Column(
            "parent_id",
            sa.String(36),
            sa.ForeignKey("document_node.id"),
            nullable=True,
        ),
        sa.Column("node_type", sa.String(32), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("sort_key", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_document_node_project_parent_sort",
        "document_node",
        ["project_id", "parent_id", "sort_key"],
    )
    roles = [
        ("mandatory_content", "Conteúdo obrigatório"),
        ("supporting_context", "Contexto de apoio"),
        ("constraint", "Restrição"),
        ("example", "Exemplo"),
        ("cross_reference", "Referência cruzada"),
        ("verification_basis", "Base de verificação"),
        ("open_issue", "Questão em aberto"),
        ("excluded_content", "Conteúdo excluído"),
    ]
    import uuid

    role_table = sa.table(
        "association_role",
        sa.column("id", sa.String),
        sa.column("code", sa.String),
        sa.column("label", sa.String),
    )
    op.bulk_insert(
        role_table,
        [{"id": str(uuid.uuid4()), "code": code, "label": label} for code, label in roles],
    )

    op.create_table(
        "document_association",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "document_node_id",
            sa.String(36),
            sa.ForeignKey("document_node.id"),
            nullable=False,
        ),
        sa.Column(
            "knowledge_item_id",
            sa.String(36),
            sa.ForeignKey("knowledge_item.id"),
            nullable=False,
        ),
        sa.Column(
            "role_id",
            sa.String(36),
            sa.ForeignKey("association_role.id"),
            nullable=False,
        ),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("usage_instruction", sa.Text(), nullable=True),
        sa.Column("pinned_revision_num", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("document_association")
    op.drop_index("ix_document_node_project_parent_sort", table_name="document_node")
    op.drop_table("document_node")
    op.drop_table("association_role")