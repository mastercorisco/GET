from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.config import AppSettings
from app.models.knowledge import (
    KnowledgeDraft,
    KnowledgeItem,
    KnowledgeRelation,
    KnowledgeRevision,
    Library,
    LibraryVersion,
    RelationType,
)
from app.schemas.knowledge import (
    DraftUpdateRequest,
    KnowledgeCreateRequest,
    KnowledgeResponse,
    RelationCreateRequest,
    RelationResponse,
    RevisionResponse,
)
from app.services.workspace_service import workspace_session

_RELATION_TYPES = (
    ("depends_on", "Depende de"),
    ("related_to", "Relacionado com"),
    ("supersedes", "Substitui"),
)


class KnowledgeError(Exception):
    pass


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _ensure_library(session: Session) -> Library:
    library = session.scalar(select(Library).limit(1))
    if library is None:
        library = Library(name="Biblioteca EDA", created_at=_utcnow())
        session.add(library)
        session.flush()
        session.add(
            LibraryVersion(
                library_id=library.id,
                version=1,
                published_at=_utcnow(),
            )
        )
    existing = {row.code for row in session.scalars(select(RelationType))}
    for code, label in _RELATION_TYPES:
        if code not in existing:
            session.add(RelationType(code=code, label=label))
    session.flush()
    return library


def _revisions(session: Session, item_id: str) -> list[KnowledgeRevision]:
    return list(
        session.scalars(
            select(KnowledgeRevision)
            .where(KnowledgeRevision.item_id == item_id)
            .order_by(KnowledgeRevision.revision_num)
        )
    )


def _status_label(revisions: list[KnowledgeRevision]) -> str:
    if not revisions:
        return "rascunho"
    latest = revisions[-1]
    return f"revisão {latest.revision_num} · {latest.maturity}/{latest.approval}/{latest.lifecycle}"


def _relations(session: Session, item_id: str) -> list[RelationResponse]:
    rows = session.execute(
        select(KnowledgeRelation, RelationType.code)
        .join(RelationType, RelationType.id == KnowledgeRelation.relation_type_id)
        .where(
            (KnowledgeRelation.source_item_id == item_id)
            | (KnowledgeRelation.target_item_id == item_id)
        )
    ).all()
    return [
        RelationResponse(
            id=relation.id,
            relation_type=code,
            source_item_id=relation.source_item_id,
            target_item_id=relation.target_item_id,
        )
        for relation, code in rows
    ]


def _to_response(session: Session, item: KnowledgeItem, draft: KnowledgeDraft) -> KnowledgeResponse:
    revisions = _revisions(session, item.id)
    latest = revisions[-1] if revisions else None
    return KnowledgeResponse(
        id=item.id,
        scope_type="library",
        scope_id=item.scope_id,
        human_code=item.human_code,
        title=draft.title,
        content=draft.content_md,
        origin_context=draft.origin_context,
        knowledge_type=draft.knowledge_type,
        maturity=latest.maturity if latest else draft.maturity,
        approval=latest.approval if latest else draft.approval,
        lifecycle=latest.lifecycle if latest else draft.lifecycle,
        status_label=_status_label(revisions),
        revision_count=len(revisions),
        latest_revision_num=latest.revision_num if latest else None,
        revisions=[
            RevisionResponse(
                id=revision.id,
                revision_num=revision.revision_num,
                title=revision.title,
                content=revision.content_md,
                origin_context=revision.origin_context,
                knowledge_type=revision.knowledge_type,
                maturity=revision.maturity,
                approval=revision.approval,
                lifecycle=revision.lifecycle,
            )
            for revision in revisions
        ],
        relations=_relations(session, item.id),
    )


def _require_item(session: Session, item_id: str) -> tuple[KnowledgeItem, KnowledgeDraft]:
    item = session.get(KnowledgeItem, item_id)
    if item is None or item.scope_type != "library":
        raise KnowledgeError("Unidade não encontrada.")
    draft = session.get(KnowledgeDraft, item_id)
    if draft is None:
        raise KnowledgeError("Rascunho em falta.")
    return item, draft


def _replace_draft_index(session: Session, draft: KnowledgeDraft) -> None:
    session.execute(
        text("DELETE FROM knowledge_revision_fts WHERE item_id = :item_id AND kind = 'draft'"),
        {"item_id": draft.item_id},
    )
    session.execute(
        text(
            """
            INSERT INTO knowledge_revision_fts(item_id, kind, title, content, origin_context)
            VALUES (:item_id, 'draft', :title, :content, :origin_context)
            """
        ),
        {
            "item_id": draft.item_id,
            "title": draft.title,
            "content": draft.content_md,
            "origin_context": draft.origin_context,
        },
    )


def list_items(app_settings: AppSettings) -> list[KnowledgeResponse]:
    with workspace_session(app_settings) as (session, _paths):
        _ensure_library(session)
        items = list(
            session.scalars(
                select(KnowledgeItem)
                .where(KnowledgeItem.scope_type == "library")
                .order_by(KnowledgeItem.created_at)
            )
        )
        result: list[KnowledgeResponse] = []
        for item in items:
            draft = session.get(KnowledgeDraft, item.id)
            if draft is None:
                continue
            result.append(_to_response(session, item, draft))
        return result


def get_item(app_settings: AppSettings, item_id: str) -> KnowledgeResponse:
    with workspace_session(app_settings) as (session, _paths):
        _ensure_library(session)
        item, draft = _require_item(session, item_id)
        return _to_response(session, item, draft)


def create_item(app_settings: AppSettings, body: KnowledgeCreateRequest) -> KnowledgeResponse:
    with workspace_session(app_settings) as (session, _paths):
        library = _ensure_library(session)
        item = KnowledgeItem(
            id=str(uuid.uuid4()),
            scope_type="library",
            scope_id=library.id,
            human_code=body.human_code,
            created_at=_utcnow(),
        )
        draft = KnowledgeDraft(
            item_id=item.id,
            title=body.title.strip(),
            content_md=body.content.strip(),
            origin_context=body.origin_context.strip(),
            knowledge_type=body.knowledge_type,
            maturity=body.maturity,
            approval=body.approval,
            lifecycle=body.lifecycle,
            updated_at=_utcnow(),
        )
        session.add(item)
        session.flush()
        session.add(draft)
        session.flush()
        _replace_draft_index(session, draft)
        return _to_response(session, item, draft)


def update_draft(app_settings: AppSettings, item_id: str, body: DraftUpdateRequest) -> KnowledgeResponse:
    with workspace_session(app_settings) as (session, _paths):
        _ensure_library(session)
        item, draft = _require_item(session, item_id)
        draft.title = body.title.strip()
        draft.content_md = body.content.strip()
        draft.origin_context = body.origin_context.strip()
        draft.knowledge_type = body.knowledge_type
        draft.maturity = body.maturity
        draft.approval = body.approval
        draft.lifecycle = body.lifecycle
        draft.updated_at = _utcnow()
        _replace_draft_index(session, draft)
        return _to_response(session, item, draft)


def conclude_revision(app_settings: AppSettings, item_id: str) -> KnowledgeResponse:
    with workspace_session(app_settings) as (session, _paths):
        _ensure_library(session)
        item, draft = _require_item(session, item_id)
        previous = _revisions(session, item.id)
        revision_num = (previous[-1].revision_num + 1) if previous else 1
        revision = KnowledgeRevision(
            item_id=item.id,
            revision_num=revision_num,
            title=draft.title,
            content_md=draft.content_md,
            origin_context=draft.origin_context,
            knowledge_type=draft.knowledge_type,
            maturity=draft.maturity,
            approval=draft.approval,
            lifecycle=draft.lifecycle,
            created_at=_utcnow(),
        )
        session.add(revision)
        session.flush()
        session.execute(
            text(
                """
                INSERT INTO knowledge_revision_fts(item_id, kind, title, content, origin_context)
                VALUES (:item_id, 'revision', :title, :content, :origin_context)
                """
            ),
            {
                "item_id": item.id,
                "title": revision.title,
                "content": revision.content_md,
                "origin_context": revision.origin_context,
            },
        )
        return _to_response(session, item, draft)


def create_relation(app_settings: AppSettings, body: RelationCreateRequest) -> RelationResponse:
    if body.source_item_id == body.target_item_id:
        raise KnowledgeError("Uma unidade não pode relacionar-se consigo própria.")
    with workspace_session(app_settings) as (session, _paths):
        _ensure_library(session)
        _require_item(session, body.source_item_id)
        _require_item(session, body.target_item_id)
        relation_type = session.scalar(select(RelationType).where(RelationType.code == body.relation_type))
        if relation_type is None:
            raise KnowledgeError("Tipo de relação desconhecido.")
        relation = KnowledgeRelation(
            relation_type_id=relation_type.id,
            source_item_id=body.source_item_id,
            target_item_id=body.target_item_id,
            created_at=_utcnow(),
        )
        session.add(relation)
        session.flush()
        return RelationResponse(
            id=relation.id,
            relation_type=relation_type.code,
            source_item_id=relation.source_item_id,
            target_item_id=relation.target_item_id,
        )


def _fts_query(raw: str) -> str:
    tokens = re.findall(r"[\w]+", raw, flags=re.UNICODE)
    if not tokens:
        raise KnowledgeError("Consulta de pesquisa vazia.")
    return " AND ".join(f'"{token}"' for token in tokens)


def search_items(app_settings: AppSettings, query: str, scope_type: str = "library") -> list[KnowledgeResponse]:
    if scope_type != "library":
        raise KnowledgeError("Nesta fase a pesquisa só cobre a biblioteca.")
    match = _fts_query(query)
    with workspace_session(app_settings) as (session, _paths):
        _ensure_library(session)
        rows = session.execute(
            text(
                """
                SELECT DISTINCT item_id
                FROM knowledge_revision_fts
                WHERE knowledge_revision_fts MATCH :match
                """
            ),
            {"match": match},
        ).all()
        result: list[KnowledgeResponse] = []
        for (item_id,) in rows:
            item = session.get(KnowledgeItem, item_id)
            if item is None or item.scope_type != scope_type:
                continue
            draft = session.get(KnowledgeDraft, item.id)
            if draft is None:
                continue
            result.append(_to_response(session, item, draft))
        return result
