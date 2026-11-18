"""Lock em memória para operações exclusivas no workspace (um processo, um get.db)."""

from __future__ import annotations

import threading
from contextlib import contextmanager
from typing import Iterator

_lock = threading.Lock()
_holder: str | None = None


class WorkspaceExclusiveError(Exception):
    def __init__(self, message: str, *, operation: str | None = None) -> None:
        super().__init__(message)
        self.operation = operation


@contextmanager
def workspace_exclusive(operation: str) -> Iterator[None]:
    global _holder
    if not _lock.acquire(blocking=False):
        active = _holder or "desconhecida"
        raise WorkspaceExclusiveError(
            f"Operação de workspace em curso ({active}). Aguarde e tente de novo.",
            operation=active,
        )
    _holder = operation
    try:
        yield
    finally:
        _holder = None
        _lock.release()