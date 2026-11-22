from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.block.export import find_fascicle_id, resolved_premises_for_point
from app.domain.block.models import DevelopmentPoint
from app.domain.block.schemas import PointLists
from app.models.document import DocumentNode
from app.models.project import Project
from app.models.workspace import WorkspaceSettings
from app.schemas.structure_export import (
    BlockModelSnapshot,
    DocumentStructureSnapshotV1,
    PointFullSnapshot,
    PointSummarySnapshot,
    StructureExportOptionsSnapshot,
    StructureExportRequest,
    StructureTreeNodeSnapshot,
)
from app.services.document_service import compute_display_codes


class StructureExportError(Exception):
    pass


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _local_user(session: Session) -> str:
    settings = session.scalar(select(WorkspaceSettings).limit(1))
    return settings.local_user_name if settings else "local_user"


def _children_map(nodes: list[DocumentNode]) -> dict[str | None, list[DocumentNode]]:
    grouped: dict[str | None, list[DocumentNode]] = {}
    for node in nodes:
        grouped.setdefault(node.parent_id, []).append(node)
    for kids in grouped.values():
        kids.sort(key=lambda n: (n.sort_key, n.id))
    return grouped


def _subtree_ids(nodes_by_id: dict[str, DocumentNode], root_id: str) -> set[str]:
    children: dict[str, list[str]] = {}
    for n in nodes_by_id.values():
        if n.parent_id:
            children.setdefault(n.parent_id, []).append(n.id)
    result = {root_id}
    stack = [root_id]
    while stack:
        cur = stack.pop()
        for kid in children.get(cur, []):
            if kid not in result:
                result.add(kid)
                stack.append(kid)
    return result


def _parse_lists(raw: str) -> PointLists:
    try:
        data = json.loads(raw) if raw else {}
    except json.JSONDecodeError:
        data = {}
    return PointLists.model_validate(data)


def _block_model(node: DocumentNode) -> BlockModelSnapshot:
    try:
        target = json.loads(node.target_output_json or "{}")
    except json.JSONDecodeError:
        target = {}
    return BlockModelSnapshot(
        objective=node.objective or "",
        scope=node.scope or "",
        target_output=target if isinstance(target, dict) else {},
        block_status=node.block_status or "active",
    )


def _load_points(
    session: Session,
    block: DocumentNode,
    *,
    point_detail: str,
    include_premises: bool,
) -> list[PointSummarySnapshot] | list[PointFullSnapshot] | None:
    if point_detail == "none":
        return None
    rows = list(
        session.scalars(
            select(DevelopmentPoint)
            .where(DevelopmentPoint.block_id == block.id)
            .where(DevelopmentPoint.status != "obsolete")
            .order_by(DevelopmentPoint.sort_order, DevelopmentPoint.id)
        )
    )
    if point_detail == "summary":
        out: list[PointSummarySnapshot] = []
        for p in rows:
            lists = _parse_lists(p.lists_json)
            out.append(
                PointSummarySnapshot(
                    id=p.id,
                    order=p.sort_order,
                    title=p.title,
                    status=p.status,
                    llm_freedom=p.llm_freedom,
                    premise_count=0,
                    must_include_count=len(lists.must_include),
                    open_questions_count=len(lists.open_questions),
                    acceptance_criteria_count=len(lists.acceptance_criteria),
                )
            )
        return out
    fascicle_id = find_fascicle_id(session, block)
    full: list[PointFullSnapshot] = []
    for p in rows:
        lists = _parse_lists(p.lists_json)
        premises: list[dict[str, Any]] = []
        if include_premises:
            premises = resolved_premises_for_point(
                session, block.project_id, fascicle_id, block.id, p.id
            )
        full.append(
            PointFullSnapshot(
                id=p.id,
                order=p.sort_order,
                title=p.title,
                core_idea=p.core_idea,
                intended_outcome=p.intended_outcome,
                llm_freedom=p.llm_freedom,
                status=p.status,
                template_id=p.template_id,
                needs_review=p.needs_review,
                lists=lists.model_dump(),
                premises=premises,
            )
        )
    return full


def _node_depth(node_id: str, by_id: dict[str, DocumentNode]) -> int:
    depth = 0
    cur = by_id.get(node_id)
    while cur and cur.parent_id:
        depth += 1
        cur = by_id.get(cur.parent_id)
    return depth


def _build_tree_node(
    session: Session,
    node: DocumentNode,
    by_id: dict[str, DocumentNode],
    children_map: dict[str | None, list[DocumentNode]],
    codes: dict[str, str],
    request: StructureExportRequest,
    *,
    depth: int,
) -> StructureTreeNodeSnapshot:
    block_model = None
    points = None
    if node.node_type == "block":
        if request.include_block_model:
            block_model = _block_model(node)
        points = _load_points(
            session,
            node,
            point_detail=request.point_detail,
            include_premises=request.include_point_premises,
        )
    children = []
    for child in children_map.get(node.id, []):
        children.append(
            _build_tree_node(
                session,
                child,
                by_id,
                children_map,
                codes,
                request,
                depth=depth + 1,
            )
        )
    block_status = (node.block_status or "active") if node.node_type == "block" else None
    return StructureTreeNodeSnapshot(
        id=node.id,
        node_type=node.node_type,
        display_code=codes.get(node.id, ""),
        title=node.title,
        depth=depth,
        sort_key=node.sort_key,
        block_status=block_status,
        block_model=block_model,
        points=points,
        children=children,
    )


def collect_snapshot(
    session: Session,
    project_id: str,
    request: StructureExportRequest,
) -> DocumentStructureSnapshotV1:
    project = session.get(Project, project_id)
    if project is None:
        raise StructureExportError("Projeto não encontrado.")

    nodes = list(session.scalars(select(DocumentNode).where(DocumentNode.project_id == project_id)))
    if not nodes:
        raise StructureExportError("Estrutura documental vazia.")

    by_id = {n.id: n for n in nodes}
    codes = compute_display_codes(nodes)
    children_map = _children_map(nodes)

    allowed_ids: set[str] | None = None
    root_node: DocumentNode | None = None

    if request.root_node_id:
        root_node = by_id.get(request.root_node_id)
        if root_node is None:
            raise StructureExportError("Nó raiz inválido para este projecto.")
        allowed_ids = _subtree_ids(by_id, root_node.id)
        tree = _build_tree_node(
            session,
            root_node,
            by_id,
            children_map,
            codes,
            request,
            depth=0,
        )
        root_display = codes.get(root_node.id, "")
        root_title = root_node.title
        root_id = root_node.id
    else:
        fascicles = children_map.get(None, [])
        fascicles = [f for f in fascicles if f.node_type == "fascicle"]
        if not fascicles:
            raise StructureExportError("Nenhum fascículo na raiz do projecto.")
        tree_children = [
            _build_tree_node(session, f, by_id, children_map, codes, request, depth=1)
            for f in fascicles
        ]
        tree = StructureTreeNodeSnapshot(
            id=project_id,
            node_type="project",
            display_code="",
            title=project.name,
            depth=0,
            sort_key=0,
            children=tree_children,
        )
        root_id = None
        root_display = ""
        root_title = project.name

    return DocumentStructureSnapshotV1(
        project_id=project_id,
        project_name=project.name,
        root_node_id=root_id,
        root_display_code=root_display,
        root_title=root_title,
        exported_at=_utcnow_iso(),
        exported_by=_local_user(session),
        options=StructureExportOptionsSnapshot(
            include_block_model=request.include_block_model,
            point_detail=request.point_detail,
            include_point_premises=request.include_point_premises,
            format=request.format,
        ),
        tree=tree,
    )