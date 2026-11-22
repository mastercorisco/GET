from __future__ import annotations

from sqlalchemy import delete, func, or_, select, text
from sqlalchemy.orm import Session

from app.config import AppSettings
from app.domain.block.models import DevelopmentPoint, Premise
from app.models.baseline import Baseline, BaselineDocumentCode, BaselineEntry, ExportRecord
from app.models.document import DocumentAssociation, DocumentNode
from app.models.imports import (
    ChangeDecision,
    ChangeProposal,
    ImportQuarantineItem,
    ImportRecord,
    ImportStagingItem,
    MergeSession,
)
from app.models.knowledge import (
    KnowledgeDraft,
    KnowledgeItem,
    KnowledgeItemAlias,
    KnowledgeRelation,
    KnowledgeRevision,
)
from app.models.project import Project, ProjectLibraryPin
from app.models.reference import Reference, StandardProfile
from app.models.technical import TechnicalInstance
from app.models.technical_profile import TechnicalProfileDraft, TechnicalProfilePayload
from app.models.terminology import ProjectTerminologyOverride, TerminologyConcept
from app.domain.block.export import load_premises
from app.services.document_service import DocumentError
from app.services.knowledge_service import KnowledgeError, _ensure_library, _revisions
from app.services.project_service import ProjectError
from app.services.reference_service import ReferenceError
from app.services.technical_service import TechnicalError
from app.services.terminology_service import TerminologyError
from app.services.workspace_exclusivity import workspace_exclusive
from app.services.workspace_service import workspace_session

_DOCUMENT_PURGE_BATCH = 40


class DeletionResult:
    def __init__(self, mode: str, detail: str | None = None) -> None:
        self.mode = mode
        self.detail = detail


def _hard_delete_knowledge(session: Session, item_id: str) -> None:
    revision_ids = list(
        session.scalars(select(KnowledgeRevision.id).where(KnowledgeRevision.item_id == item_id))
    )
    if revision_ids:
        session.execute(
            delete(TechnicalProfilePayload).where(TechnicalProfilePayload.revision_id.in_(revision_ids))
        )
    session.execute(delete(KnowledgeRevision).where(KnowledgeRevision.item_id == item_id))
    session.execute(
        delete(KnowledgeRelation).where(
            or_(
                KnowledgeRelation.source_item_id == item_id,
                KnowledgeRelation.target_item_id == item_id,
            )
        )
    )
    session.execute(delete(KnowledgeItemAlias).where(KnowledgeItemAlias.item_id == item_id))
    session.execute(delete(TechnicalProfileDraft).where(TechnicalProfileDraft.item_id == item_id))
    session.execute(delete(KnowledgeDraft).where(KnowledgeDraft.item_id == item_id))
    session.execute(text("DELETE FROM knowledge_revision_fts WHERE item_id = :id"), {"id": item_id})
    session.execute(delete(DocumentAssociation).where(DocumentAssociation.knowledge_item_id == item_id))
    item = session.get(KnowledgeItem, item_id)
    if item is not None:
        session.delete(item)


def delete_knowledge_item(app_settings: AppSettings, item_id: str) -> DeletionResult:
    with workspace_session(app_settings) as (session, _paths):
        _ensure_library(session)
        item = session.get(KnowledgeItem, item_id)
        if item is None:
            raise KnowledgeError("Unidade não encontrada.")
        draft = session.get(KnowledgeDraft, item_id)
        if draft is None:
            raise KnowledgeError("Rascunho em falta.")
        revisions = _revisions(session, item_id)
        assoc_count = session.scalar(
            select(func.count())
            .select_from(DocumentAssociation)
            .where(DocumentAssociation.knowledge_item_id == item_id)
        )
        if revisions or (assoc_count or 0) > 0 or draft.approval not in {"unreviewed", "rejected"}:
            draft.lifecycle = "archived"
            for rev in revisions:
                rev.lifecycle = "archived"
            session.flush()
            return DeletionResult("archived", "Unidade arquivada (tinha revisões ou associações).")
        _hard_delete_knowledge(session, item_id)
        session.flush()
        return DeletionResult("deleted", "Rascunho eliminado.")


def delete_knowledge_relation(app_settings: AppSettings, relation_id: str) -> None:
    with workspace_session(app_settings) as (session, _paths):
        _ensure_library(session)
        row = session.get(KnowledgeRelation, relation_id)
        if row is None:
            raise KnowledgeError("Relação não encontrada.")
        session.delete(row)


def delete_reference(app_settings: AppSettings, reference_id: str) -> None:
    with workspace_session(app_settings) as (session, _paths):
        ref = session.get(Reference, reference_id)
        if ref is None:
            raise ReferenceError("Referência não encontrada.")
        session.execute(delete(StandardProfile).where(StandardProfile.reference_id == reference_id))
        session.delete(ref)


def delete_terminology(app_settings: AppSettings, concept_id: str) -> None:
    with workspace_session(app_settings) as (session, _paths):
        row = session.get(TerminologyConcept, concept_id)
        if row is None:
            raise TerminologyError("Termo não encontrado.")
        override = session.scalar(
            select(ProjectTerminologyOverride).where(ProjectTerminologyOverride.concept_id == concept_id)
        )
        if override is not None:
            raise TerminologyError("Termo com override em projecto — apague o override primeiro.")
        session.delete(row)


def delete_terminology_override(app_settings: AppSettings, project_id: str, override_id: str) -> None:
    with workspace_session(app_settings) as (session, _paths):
        row = session.get(ProjectTerminologyOverride, override_id)
        if row is None or row.project_id != project_id:
            raise TerminologyError("Override não encontrado.")
        session.delete(row)


def _delete_premises_for_owner(session: Session, owner_kind: str, owner_id: str) -> None:
    for prem in load_premises(session, owner_kind, owner_id):
        session.delete(prem)


def _delete_block_points(session: Session, block_id: str) -> None:
    points = list(session.scalars(select(DevelopmentPoint).where(DevelopmentPoint.block_id == block_id)))
    for point in points:
        _delete_premises_for_owner(session, "development_point", point.id)
        session.delete(point)


def _subtree_ids(session: Session, project_id: str, root_id: str) -> list[str]:
    nodes = list(
        session.scalars(select(DocumentNode).where(DocumentNode.project_id == project_id))
    )
    by_parent: dict[str | None, list[DocumentNode]] = {}
    for n in nodes:
        by_parent.setdefault(n.parent_id, []).append(n)
    result: list[str] = []

    def walk(nid: str) -> None:
        result.append(nid)
        for child in by_parent.get(nid, []):
            walk(child.id)

    walk(root_id)
    return result


def _baseline_blocks_node(session: Session, node_ids: list[str]) -> bool:
    if not node_ids:
        return False
    count = session.scalar(
        select(func.count())
        .select_from(BaselineDocumentCode)
        .where(BaselineDocumentCode.document_node_id.in_(node_ids))
    )
    return bool(count)


def delete_document_node(app_settings: AppSettings, project_id: str, node_id: str) -> None:
    with workspace_session(app_settings) as (session, _paths):
        node = session.get(DocumentNode, node_id)
        if node is None or node.project_id != project_id:
            raise DocumentError("Nó documental não encontrado.")
        subtree = _subtree_ids(session, project_id, node_id)
        if _baseline_blocks_node(session, subtree):
            raise DocumentError("Estrutura referenciada numa baseline — não pode ser eliminada.")
        for nid in reversed(subtree):
            sub = session.get(DocumentNode, nid)
            if sub is None:
                continue
            if sub.node_type == "block":
                _delete_block_points(session, nid)
            _delete_premises_for_owner(session, "block", nid)
            _delete_premises_for_owner(session, "fascicle", nid)
            session.execute(
                delete(DocumentAssociation).where(DocumentAssociation.document_node_id == nid)
            )
            session.delete(sub)
        session.flush()


def delete_document_association(app_settings: AppSettings, association_id: str) -> None:
    with workspace_session(app_settings) as (session, _paths):
        row = session.get(DocumentAssociation, association_id)
        if row is None:
            raise DocumentError("Associação não encontrada.")
        session.delete(row)


def delete_technical_instance(app_settings: AppSettings, project_id: str, instance_id: str) -> None:
    with workspace_session(app_settings) as (session, _paths):
        row = session.get(TechnicalInstance, instance_id)
        if row is None or row.project_id != project_id:
            raise TechnicalError("Instância não encontrada.")
        child_count = session.scalar(
            select(func.count())
            .select_from(TechnicalInstance)
            .where(TechnicalInstance.parent_id == instance_id)
        )
        if child_count:
            raise TechnicalError("Apague primeiro as instâncias filhas.")
        session.delete(row)


def _purge_merge_sessions_for_project(session: Session, project_id: str) -> int:
    merges = list(session.scalars(select(MergeSession).where(MergeSession.project_id == project_id)))
    if not merges:
        return 0
    for merge in merges:
        props = list(
            session.scalars(select(ChangeProposal).where(ChangeProposal.merge_session_id == merge.id))
        )
        for prop in props:
            session.execute(delete(ChangeDecision).where(ChangeDecision.proposal_id == prop.id))
        session.execute(delete(ChangeProposal).where(ChangeProposal.merge_session_id == merge.id))
    session.execute(delete(MergeSession).where(MergeSession.project_id == project_id))
    session.flush()
    return len(merges)


def _purge_imports(session: Session, project_id: str) -> None:
    imports = list(session.scalars(select(ImportRecord).where(ImportRecord.project_id == project_id)))
    for imp in imports:
        merges = list(session.scalars(select(MergeSession).where(MergeSession.import_id == imp.id)))
        for merge in merges:
            props = list(
                session.scalars(select(ChangeProposal).where(ChangeProposal.merge_session_id == merge.id))
            )
            for prop in props:
                session.execute(delete(ChangeDecision).where(ChangeDecision.proposal_id == prop.id))
            session.execute(delete(ChangeProposal).where(ChangeProposal.merge_session_id == merge.id))
        session.execute(delete(MergeSession).where(MergeSession.import_id == imp.id))
        session.execute(delete(ImportStagingItem).where(ImportStagingItem.import_id == imp.id))
        session.execute(delete(ImportQuarantineItem).where(ImportQuarantineItem.import_id == imp.id))
        session.delete(imp)


def _purge_baselines_and_exports(session: Session, project_id: str) -> None:
    exports = list(session.scalars(select(ExportRecord).where(ExportRecord.project_id == project_id)))
    for row in exports:
        row.parent_export_id = None
    session.flush()
    for row in exports:
        session.delete(row)
    session.flush()
    baselines = list(session.scalars(select(Baseline).where(Baseline.project_id == project_id)))
    for baseline in baselines:
        session.execute(delete(BaselineEntry).where(BaselineEntry.baseline_id == baseline.id))
        session.execute(delete(BaselineDocumentCode).where(BaselineDocumentCode.baseline_id == baseline.id))
        session.delete(baseline)


def _require_project(session: Session, project_id: str) -> Project:
    project = session.get(Project, project_id)
    if project is None:
        raise ProjectError("Projeto não encontrado.")
    return project


def _purge_project_development_points(session: Session, project_id: str) -> int:
    block_ids = select(DocumentNode.id).where(
        DocumentNode.project_id == project_id,
        DocumentNode.node_type == "block",
    )
    point_ids = select(DevelopmentPoint.id).where(DevelopmentPoint.block_id.in_(block_ids))
    session.execute(
        delete(Premise).where(
            Premise.owner_kind == "development_point",
            Premise.owner_id.in_(point_ids),
        )
    )
    res = session.execute(delete(DevelopmentPoint).where(DevelopmentPoint.block_id.in_(block_ids)))
    session.flush()
    return res.rowcount if res.rowcount is not None else 0


def _purge_document_nodes_batch(
    session: Session, project_id: str, *, limit: int, node_type: str | None = None
) -> int:
    nodes = list(session.scalars(select(DocumentNode).where(DocumentNode.project_id == project_id)))
    if node_type is not None:
        nodes = [n for n in nodes if n.node_type == node_type]
    if not nodes:
        return 0
    parent_ids = {n.parent_id for n in nodes if n.parent_id}
    leaves = [n for n in nodes if n.id not in parent_ids]
    if not leaves:
        _purge_document_subtree(session, project_id, nodes[0].id)
        return 1
    targets = leaves[:limit]
    node_ids = [n.id for n in targets]
    for nid in node_ids:
        node = session.get(DocumentNode, nid)
        if node is None:
            continue
        if node.node_type == "block":
            _delete_block_points(session, nid)
        _delete_premises_for_owner(session, "block", nid)
        _delete_premises_for_owner(session, "fascicle", nid)
    session.execute(delete(DocumentAssociation).where(DocumentAssociation.document_node_id.in_(node_ids)))
    session.execute(delete(DocumentNode).where(DocumentNode.id.in_(node_ids)))
    session.flush()
    return len(node_ids)


def _purge_document_subtree(session: Session, project_id: str, root_id: str) -> None:
    for nid in reversed(_subtree_ids(session, project_id, root_id)):
        sub = session.get(DocumentNode, nid)
        if sub is None:
            continue
        if sub.node_type == "block":
            _delete_block_points(session, nid)
        _delete_premises_for_owner(session, "block", nid)
        _delete_premises_for_owner(session, "fascicle", nid)
        session.execute(delete(DocumentAssociation).where(DocumentAssociation.document_node_id == nid))
        session.execute(delete(DocumentNode).where(DocumentNode.id == nid))
        session.flush()


def _purge_document_tree(session: Session, project_id: str) -> None:
    _purge_merge_sessions_for_project(session, project_id)
    _purge_project_development_points(session, project_id)
    while True:
        root_id = session.scalar(
            select(DocumentNode.id).where(
                DocumentNode.project_id == project_id,
                DocumentNode.node_type == "fascicle",
            )
        )
        if root_id is None:
            break
        _purge_document_subtree(session, project_id, root_id)
    while _purge_document_nodes_batch(session, project_id, limit=_DOCUMENT_PURGE_BATCH) > 0:
        pass


def purge_project_document_structure(app_settings: AppSettings, project_id: str) -> dict[str, int]:
    """Remove árvore documental, pontos, associações, baselines/export do projecto; mantém o registo Project."""
    import json

    with workspace_exclusive("purge_document_structure"):
        remaining_before = 0
        with workspace_session(app_settings, begin_immediate=True) as (session, _paths):
            _require_project(session, project_id)
            remaining_before = session.scalar(
                select(func.count()).select_from(DocumentNode).where(DocumentNode.project_id == project_id)
            ) or 0
            _purge_imports(session, project_id)
            _purge_baselines_and_exports(session, project_id)
        with workspace_session(app_settings, begin_immediate=True) as (session, _paths):
            _require_project(session, project_id)
            _purge_document_tree(session, project_id)
        with workspace_session(app_settings, begin_immediate=True) as (session, _paths):
            project = _require_project(session, project_id)
            try:
                ctx = json.loads(project.llm_context_json or "{}")
            except json.JSONDecodeError:
                ctx = {}
            if not isinstance(ctx, dict):
                ctx = {}
            ctx.pop("structure_catalog", None)
            project.llm_context_json = json.dumps(ctx, ensure_ascii=False, sort_keys=True)
            session.flush()
            remaining_after = session.scalar(
                select(func.count()).select_from(DocumentNode).where(DocumentNode.project_id == project_id)
            ) or 0
            points_left = session.scalar(
                select(func.count())
                .select_from(DevelopmentPoint)
                .join(DocumentNode, DevelopmentPoint.block_id == DocumentNode.id)
                .where(DocumentNode.project_id == project_id)
            ) or 0
        return {
            "document_nodes_removed": remaining_before,
            "document_nodes_remaining": remaining_after,
            "development_points_remaining": points_left,
        }


def _purge_technical_leaves_batch(session: Session, project_id: str, *, max_deletes: int) -> int:
    instances = list(
        session.scalars(select(TechnicalInstance).where(TechnicalInstance.project_id == project_id))
    )
    if not instances:
        return 0
    parent_ids = set(
        session.scalars(
            select(TechnicalInstance.parent_id).where(
                TechnicalInstance.project_id == project_id,
                TechnicalInstance.parent_id.isnot(None),
            )
        )
    )
    leaves = [i for i in instances if i.id not in parent_ids]
    if not leaves:
        targets = instances[:max_deletes]
    else:
        targets = leaves[:max_deletes]
    for inst in targets:
        session.delete(inst)
    session.flush()
    return len(targets)


def _purge_project_tail(session: Session, project_id: str) -> None:
    items = list(
        session.scalars(
            select(KnowledgeItem).where(
                KnowledgeItem.scope_type == "project",
                KnowledgeItem.scope_id == project_id,
            )
        )
    )
    for item in items:
        _hard_delete_knowledge(session, item.id)
    session.execute(
        delete(ProjectTerminologyOverride).where(ProjectTerminologyOverride.project_id == project_id)
    )
    session.execute(
        delete(TerminologyConcept).where(
            TerminologyConcept.scope_type == "project",
            TerminologyConcept.scope_id == project_id,
        )
    )
    session.execute(delete(Reference).where(Reference.scope_type == "project", Reference.scope_id == project_id))
    _delete_premises_for_owner(session, "project", project_id)
    session.execute(delete(ProjectLibraryPin).where(ProjectLibraryPin.project_id == project_id))
    project = _require_project(session, project_id)
    session.delete(project)
    session.flush()


def delete_project(app_settings: AppSettings, project_id: str) -> None:
    with workspace_exclusive("delete_project"):
        with workspace_session(app_settings, begin_immediate=True) as (session, _paths):
            _require_project(session, project_id)
        with workspace_session(app_settings, begin_immediate=True) as (session, _paths):
            _purge_imports(session, project_id)
        with workspace_session(app_settings, begin_immediate=True) as (session, _paths):
            _purge_baselines_and_exports(session, project_id)
        with workspace_session(app_settings, begin_immediate=True) as (session, _paths):
            _purge_document_tree(session, project_id)
        while True:
            with workspace_session(app_settings, begin_immediate=True) as (session, _paths):
                removed = _purge_technical_leaves_batch(session, project_id, max_deletes=_DOCUMENT_PURGE_BATCH)
                if removed == 0:
                    break
        with workspace_session(app_settings, begin_immediate=True) as (session, _paths):
            _purge_project_tail(session, project_id)