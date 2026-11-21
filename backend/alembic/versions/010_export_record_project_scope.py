"""Export record scoped by project (export_id not globally unique)

Revision ID: 010
Revises: 009
Create Date: 2026-11-21
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "010"
down_revision: Union[str, None] = "009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    if conn.dialect.name == "sqlite":
        op.execute(
            """
            CREATE TABLE export_record_new (
                id VARCHAR(36) NOT NULL PRIMARY KEY,
                project_id VARCHAR(36) NOT NULL REFERENCES project(id),
                baseline_id VARCHAR(36) NOT NULL REFERENCES baseline(id),
                export_id VARCHAR(64) NOT NULL,
                profile VARCHAR(32) NOT NULL,
                schema_name VARCHAR(64) NOT NULL,
                sha256 VARCHAR(64) NOT NULL,
                file_path TEXT NOT NULL,
                package_type VARCHAR(32) NOT NULL,
                parent_export_id VARCHAR(36) REFERENCES export_record(id),
                created_at DATETIME NOT NULL,
                CONSTRAINT uq_export_record_project_export_id UNIQUE (project_id, export_id)
            )
            """
        )
        op.execute(
            """
            INSERT INTO export_record_new (
                id, project_id, baseline_id, export_id, profile, schema_name,
                sha256, file_path, package_type, parent_export_id, created_at
            )
            SELECT
                id, project_id, baseline_id, export_id, profile, schema_name,
                sha256, file_path, package_type, parent_export_id, created_at
            FROM export_record
            """
        )
        op.execute("DROP TABLE export_record")
        op.execute("ALTER TABLE export_record_new RENAME TO export_record")
        return

    op.drop_constraint("export_record_export_id_key", "export_record", type_="unique")
    op.create_unique_constraint(
        "uq_export_record_project_export_id", "export_record", ["project_id", "export_id"]
    )


def downgrade() -> None:
    conn = op.get_bind()
    if conn.dialect.name == "sqlite":
        op.execute(
            """
            CREATE TABLE export_record_old (
                id VARCHAR(36) NOT NULL PRIMARY KEY,
                project_id VARCHAR(36) NOT NULL REFERENCES project(id),
                baseline_id VARCHAR(36) NOT NULL REFERENCES baseline(id),
                export_id VARCHAR(64) NOT NULL UNIQUE,
                profile VARCHAR(32) NOT NULL,
                schema_name VARCHAR(64) NOT NULL,
                sha256 VARCHAR(64) NOT NULL,
                file_path TEXT NOT NULL,
                package_type VARCHAR(32) NOT NULL,
                parent_export_id VARCHAR(36) REFERENCES export_record(id),
                created_at DATETIME NOT NULL
            )
            """
        )
        op.execute(
            """
            INSERT INTO export_record_old (
                id, project_id, baseline_id, export_id, profile, schema_name,
                sha256, file_path, package_type, parent_export_id, created_at
            )
            SELECT
                id, project_id, baseline_id, export_id, profile, schema_name,
                sha256, file_path, package_type, parent_export_id, created_at
            FROM export_record
            """
        )
        op.execute("DROP TABLE export_record")
        op.execute("ALTER TABLE export_record_old RENAME TO export_record")
        return

    op.drop_constraint("uq_export_record_project_export_id", "export_record", type_="unique")
    op.create_unique_constraint("export_record_export_id_key", "export_record", ["export_id"])