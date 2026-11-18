from __future__ import annotations

import sqlite3
from pathlib import Path

from app.db.session import dispose_workspace_engine, get_session_factory_for_workspace
from app.services.workspace_service import invalidate_workspace_runtime_cache


def test_invalidate_runtime_cache_after_db_replace(tmp_path: Path) -> None:
    db = tmp_path / "get.db"
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE t (x INT)")
        conn.execute("INSERT INTO t VALUES (1)")
        conn.commit()

    get_session_factory_for_workspace(db)

    with sqlite3.connect(db) as conn:
        conn.execute("DROP TABLE t")
        conn.execute("CREATE TABLE t (x INT)")
        conn.execute("INSERT INTO t VALUES (2)")
        conn.commit()

    invalidate_workspace_runtime_cache(db)
    _engine, factory = get_session_factory_for_workspace(db)
    with factory() as session:
        row = session.connection().exec_driver_sql("SELECT x FROM t").fetchone()
    assert row[0] == 2
    dispose_workspace_engine(db)