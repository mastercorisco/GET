from __future__ import annotations

import subprocess
from pathlib import Path


def test_alembic_upgrade_downgrade(tmp_path: Path) -> None:
    backend = Path(__file__).resolve().parents[2]
    db = tmp_path / "migration.db"
    env = {
        **dict(__import__("os").environ),
        "GET_ALEMBIC_URL": f"sqlite:///{db}",
    }
    subprocess.run(
        ["python3", "-m", "alembic", "upgrade", "head"],
        cwd=backend,
        check=True,
        env=env,
        capture_output=True,
    )
    subprocess.run(
        ["python3", "-m", "alembic", "downgrade", "base"],
        cwd=backend,
        check=True,
        env=env,
        capture_output=True,
    )