from __future__ import annotations

from pathlib import Path


class WorkspacePaths:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()

    @property
    def data_dir(self) -> Path:
        return self.root / "data"

    @property
    def database_path(self) -> Path:
        return self.data_dir / "get.db"

    @property
    def backups_dir(self) -> Path:
        return self.root / "backups"

    @property
    def exports_dir(self) -> Path:
        return self.root / "exports"

    @property
    def imports_dir(self) -> Path:
        return self.root / "imports"

    @property
    def migration_reports_dir(self) -> Path:
        return self.root / "migration_reports"

    def ensure_layout(self) -> None:
        for path in (
            self.data_dir,
            self.backups_dir,
            self.exports_dir,
            self.imports_dir,
            self.migration_reports_dir,
        ):
            path.mkdir(parents=True, exist_ok=True)