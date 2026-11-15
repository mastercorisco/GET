from __future__ import annotations

from collections import defaultdict

from sqlalchemy import func, select

from app.config import AppSettings
from app.models.document import AssociationRole, DocumentAssociation, DocumentNode
from app.models.knowledge import KnowledgeItem
from app.models.project import Project
from app.schemas.document import (
    AssociationCreateRequest,
    AssociationResponse,
    DocumentNodeCreateRequest,
    DocumentNodeListResponse,
    DocumentNodeMoveRequest,
    DocumentNodeMutationResponse,
    DocumentNodeResponse,
    RenumberChange,
)
from app.services.workspace_service import workspace_session

NODE_TYPES = frozenset({"fascicle", "block", "section", "subsection"})
TYPE_SUFFIX = {
    "fascicle": "F",
    "block": "B",
    "section": "S",
    "subsection": "SS",
}

_ASSOCIATION_ROLES = [
    ("mandatory_content", "Conteúdo obrigatório"),
    ("supporting_context", "Contexto de apoio"),
    ("constraint", "Restrição"),
    ("example", "Exemplo"),
    ("cross_reference", "Referência cruzada"),
    ("verification_basis", "Base de verificação"),
    ("open_issue", "Questão em aberto"),
    ("excluded_content", "Conteúdo excluído"),
]


class DocumentError(Exception):
    pass


def _ensure_association_roles(session) -> None:
    for code, label in _ASSOCIATION_ROLES:
        existing = session.scalar(select(AssociationRole).where(AssociationRole.code == code))
        if existing is None:
            session.add(AssociationRole(code=code, label=label))
    session.flush()


def _load_project_nodes(session, project_id: str) -> list[DocumentNode]:
    _ensure_association_roles(session)
    project = session.get(Project, project_id)
    if project is None:
        raise DocumentError("Projecto não encontrado.")
    return list(
        session.scalars(select(DocumentNode).where(DocumentNode.project_id == project_id).order_by(DocumentNode.sort_key))
    )


def _children_map(nodes: list[DocumentNode]) -> dict[str | None, list[DocumentNode]]:
    children: dict[str | None, list[DocumentNode]] = defaultdict(list)
    for node in nodes:
        children[node.parent_id].append(node)
    for siblings in children.values():
        siblings.sort(key=lambda n: (n.sort_key, n.created_at, n.id))
    return children


def _node_depth(node_id: str, by_id: dict[str, DocumentNode]) -> int:
    depth = 0
    current = by_id.get(node_id)
    while current is not None:
        depth += 1
        if current.parent_id is None:
            break
        current = by_id.get(current.parent_id)
    return depth


def _is_descendant(session, ancestor_id: str, node_id: str) -> bool:
    current_id: str | None = node_id
    while current_id is not None:
        if current_id == ancestor_id:
            return True
        current = session.get(DocumentNode, current_id)
        if current is None:
            break
        current_id = current.parent_id
    return False


def compute_display_codes(nodes: list[DocumentNode]) -> dict[str, str]:
    return _compute_display_codes(nodes)


def _compute_display_codes(nodes: list[DocumentNode]) -> dict[str, str]:
    children = _children_map(nodes)

    def walk(parent_id: str | None, parent_code: str | None) -> dict[str, str]:
        codes: dict[str, str] = {}
        siblings = children.get(parent_id, [])
        for index, node in enumerate(siblings, start=1):
            suffix = TYPE_SUFFIX.get(node.node_type)
            if suffix is None:
                raise DocumentError(f"Tipo de nó inválido: {node.node_type}")
            segment = f"{suffix}{index:02d}"
            if parent_code is None:
                code = segment
            else:
                code = f"{parent_code}_{segment}"
            codes[node.id] = code
            codes.update(walk(node.id, code))
        return codes

    return walk(None, None)


def _diff_codes(before: dict[str, str], after: dict[str, str]) -> list[RenumberChange]:
    changes: list[RenumberChange] = []
    all_ids = set(before) | set(after)
    for node_id in sorted(all_ids):
        old = before.get(node_id)
        new = after.get(node_id)
        if new is None:
            continue
        if old is not None and old != new:
            changes.append(RenumberChange(node_id=node_id, old_code=old, new_code=new))
    return changes


def _to_response(node: DocumentNode, codes: dict[str, str], by_id: dict[str, DocumentNode]) -> DocumentNodeResponse:
    depth = _node_depth(node.id, by_id)
    return DocumentNodeResponse(
        id=node.id,
        project_id=node.project_id,
        parent_id=node.parent_id,
        node_type=node.node_type,
        title=node.title,
        sort_key=node.sort_key,
        depth=depth,
        display_code=codes[node.id],
        depth_warning=depth >= 5,
    )


def list_document_nodes(app_settings: AppSettings, project_id: str) -> DocumentNodeListResponse:
    with workspace_session(app_settings) as (session, _paths):
        nodes = _load_project_nodes(session, project_id)
        by_id = {n.id: n for n in nodes}
        codes = _compute_display_codes(nodes)
        flat: list[DocumentNodeResponse] = []

        def walk(parent_id: str | None) -> None:
            children = _children_map(nodes).get(parent_id, [])
            for child in children:
                flat.append(_to_response(child, codes, by_id))
                walk(child.id)

        walk(None)
        return DocumentNodeListResponse(nodes=flat)


def create_document_node(
    app_settings: AppSettings, project_id: str, body: DocumentNodeCreateRequest
) -> DocumentNodeMutationResponse:
    if body.node_type not in NODE_TYPES:
        raise DocumentError("Tipo de nó inválido.")
    if body.node_type == "fascicle" and body.parent_id is not None:
        raise DocumentError("Fascículo só pode ser criado na raiz do projecto.")
    if body.node_type != "fascicle" and body.parent_id is None:
        raise DocumentError("Este tipo de nó requer um pai.")

    with workspace_session(app_settings) as (session, _paths):
        nodes_before = _load_project_nodes(session, project_id)
        codes_before = _compute_display_codes(nodes_before)

        project = session.get(Project, project_id)
        if project is None:
            raise DocumentError("Projecto não encontrado.")

        parent: DocumentNode | None = None
        if body.parent_id is not None:
            parent = session.get(DocumentNode, body.parent_id)
            if parent is None or parent.project_id != project_id:
                raise DocumentError("Nó pai inválido.")

        max_sort = session.scalar(
            select(func.max(DocumentNode.sort_key)).where(
                DocumentNode.project_id == project_id,
                DocumentNode.parent_id == body.parent_id,
            )
        )
        sort_key = (max_sort or 0) + 10

        node = DocumentNode(
            project_id=project_id,
            parent_id=body.parent_id,
            node_type=body.node_type,
            title=body.title.strip(),
            sort_key=sort_key,
        )
        session.add(node)
        session.flush()

        nodes_after = _load_project_nodes(session, project_id)
        codes_after = _compute_display_codes(nodes_after)
        by_id = {n.id: n for n in nodes_after}
        renumber = _diff_codes(codes_before, codes_after)

        return DocumentNodeMutationResponse(
            node=_to_response(node, codes_after, by_id),
            renumber_changes=renumber,
        )


def move_document_node(
    app_settings: AppSettings,
    project_id: str,
    node_id: str,
    body: DocumentNodeMoveRequest,
) -> DocumentNodeMutationResponse:
    with workspace_session(app_settings) as (session, _paths):
        nodes_before = _load_project_nodes(session, project_id)
        codes_before = _compute_display_codes(nodes_before)

        node = session.get(DocumentNode, node_id)
        if node is None or node.project_id != project_id:
            raise DocumentError("Nó documental não encontrado.")

        if body.direction in ("up", "down"):
            siblings = list(
                session.scalars(
                    select(DocumentNode)
                    .where(
                        DocumentNode.project_id == project_id,
                        DocumentNode.parent_id == node.parent_id,
                    )
                    .order_by(DocumentNode.sort_key, DocumentNode.id)
                )
            )
            index = next((i for i, s in enumerate(siblings) if s.id == node_id), None)
            if index is None:
                raise DocumentError("Nó não encontrado entre irmãos.")
            if body.direction == "up" and index > 0:
                other = siblings[index - 1]
                node.sort_key, other.sort_key = other.sort_key, node.sort_key
            elif body.direction == "down" and index < len(siblings) - 1:
                other = siblings[index + 1]
                node.sort_key, other.sort_key = other.sort_key, node.sort_key
            session.flush()
        elif body.new_parent_id is not None or body.new_sort_key is not None:
            new_parent_id = body.new_parent_id if body.new_parent_id is not None else node.parent_id
            if node.node_type == "fascicle" and new_parent_id is not None:
                raise DocumentError("Fascículo não pode ter pai.")
            if new_parent_id is not None:
                if new_parent_id == node_id:
                    raise DocumentError("Não é possível mover um nó para si próprio.")
                if _is_descendant(session, node_id, new_parent_id):
                    raise DocumentError("Não é possível mover um nó para um descendente.")
                parent = session.get(DocumentNode, new_parent_id)
                if parent is None or parent.project_id != project_id:
                    raise DocumentError("Nó pai de destino inválido.")
            node.parent_id = new_parent_id
            if body.new_sort_key is not None:
                node.sort_key = body.new_sort_key
            elif body.new_parent_id is not None and body.new_sort_key is None:
                max_sort = session.scalar(
                    select(func.max(DocumentNode.sort_key)).where(
                        DocumentNode.project_id == project_id,
                        DocumentNode.parent_id == new_parent_id,
                        DocumentNode.id != node_id,
                    )
                )
                node.sort_key = (max_sort or 0) + 10
            session.flush()
        else:
            raise DocumentError("Indique direction ou new_parent_id/new_sort_key.")

        nodes_after = _load_project_nodes(session, project_id)
        codes_after = _compute_display_codes(nodes_after)
        by_id = {n.id: n for n in nodes_after}
        moved = session.get(DocumentNode, node_id)
        if moved is None:
            raise DocumentError("Nó documental não encontrado.")
        renumber = _diff_codes(codes_before, codes_after)

        return DocumentNodeMutationResponse(
            node=_to_response(moved, codes_after, by_id),
            renumber_changes=renumber,
        )


def list_associations(app_settings: AppSettings, node_id: str) -> list[AssociationResponse]:
    with workspace_session(app_settings) as (session, _paths):
        _ensure_association_roles(session)
        node = session.get(DocumentNode, node_id)
        if node is None:
            raise DocumentError("Nó documental não encontrado.")
        rows = session.execute(
            select(DocumentAssociation, AssociationRole)
            .join(AssociationRole, AssociationRole.id == DocumentAssociation.role_id)
            .where(DocumentAssociation.document_node_id == node_id)
            .order_by(DocumentAssociation.sort_order, DocumentAssociation.id)
        )
        return [
            AssociationResponse(
                id=assoc.id,
                document_node_id=assoc.document_node_id,
                knowledge_item_id=assoc.knowledge_item_id,
                role=role.code,
                sort_order=assoc.sort_order,
                usage_instruction=assoc.usage_instruction,
                pinned_revision_num=assoc.pinned_revision_num,
            )
            for assoc, role in rows
        ]


def create_association(
    app_settings: AppSettings, node_id: str, body: AssociationCreateRequest
) -> AssociationResponse:
    with workspace_session(app_settings) as (session, _paths):
        _ensure_association_roles(session)
        node = session.get(DocumentNode, node_id)
        if node is None:
            raise DocumentError("Nó documental não encontrado.")

        item = session.get(KnowledgeItem, body.knowledge_item_id)
        if item is None:
            raise DocumentError("Unidade de conhecimento não encontrada.")

        role = session.scalar(select(AssociationRole).where(AssociationRole.code == body.role))
        if role is None:
            raise DocumentError("Papel de associação inválido.")

        max_order = session.scalar(
            select(func.max(DocumentAssociation.sort_order)).where(
                DocumentAssociation.document_node_id == node_id
            )
        )
        assoc = DocumentAssociation(
            document_node_id=node_id,
            knowledge_item_id=body.knowledge_item_id,
            role_id=role.id,
            sort_order=(max_order or 0) + 1,
            usage_instruction=body.usage_instruction,
            pinned_revision_num=body.pinned_revision_num,
        )
        session.add(assoc)
        session.flush()

        return AssociationResponse(
            id=assoc.id,
            document_node_id=assoc.document_node_id,
            knowledge_item_id=assoc.knowledge_item_id,
            role=role.code,
            sort_order=assoc.sort_order,
            usage_instruction=assoc.usage_instruction,
            pinned_revision_num=assoc.pinned_revision_num,
        )