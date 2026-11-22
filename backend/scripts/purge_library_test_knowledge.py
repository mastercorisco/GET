"""Remove unidades de conhecimento de teste na biblioteca (rascunhos sem revisões)."""
from __future__ import annotations

import os
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from sqlalchemy import select

from app.deps import get_settings
from app.models.knowledge import KnowledgeDraft, KnowledgeItem
from app.services.deletion_service import delete_knowledge_item
from app.services.workspace_service import workspace_session

DEFAULT_TITLES = frozenset(
    {
        "Semente biblioteca",
        "Semente",
        "Rascunho apagar",
        "S",
        "teste de biblioteca",
    }
)


def _titles_from_env() -> set[str]:
    extra = os.environ.get("GET_PURGE_LIBRARY_TITLES", "").strip()
    if not extra:
        return set(DEFAULT_TITLES)
    out = set(DEFAULT_TITLES)
    for part in extra.split(","):
        t = part.strip()
        if t:
            out.add(t)
    return out


def main() -> int:
    dry_run = os.environ.get("GET_PURGE_DRY_RUN", "") in ("1", "true", "yes")
    titles = _titles_from_env()
    settings = get_settings()
    with workspace_session(settings) as (session, _paths):
        rows = session.execute(
            select(KnowledgeItem.id, KnowledgeDraft.title)
            .join(KnowledgeDraft, KnowledgeDraft.item_id == KnowledgeItem.id)
            .where(KnowledgeItem.scope_type == "library")
            .where(KnowledgeDraft.title.in_(sorted(titles)))
        ).all()
    print(f"workspace: {settings.workspace_root}")
    print(f"títulos alvo ({len(titles)}): {', '.join(sorted(titles))}")
    print(f"apagar ({len(rows)}) unidades")
    for item_id, title in rows:
        print(f"  {item_id[:8]}… {title}")
    if dry_run:
        return 0
    failed: list[tuple[str, str]] = []
    for i, (item_id, title) in enumerate(rows, 1):
        try:
            result = delete_knowledge_item(settings, item_id)
            print(f"  [{i}/{len(rows)}] {result.mode} {item_id[:8]}… ({title})")
        except Exception as exc:
            failed.append((item_id, str(exc)))
            print(f"  [{i}/{len(rows)}] FAIL {item_id[:8]}…: {exc}")
    with workspace_session(settings) as (session, _paths):
        count = session.execute(
            select(KnowledgeItem.id).where(KnowledgeItem.scope_type == "library")
        ).all()
    print(f"restantes na biblioteca: {len(count)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())