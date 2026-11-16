from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import DocumentNode
from app.models.project import Project, ProjectLibraryPin
from app.services.document_service import compute_display_codes


class LlmLiveContext:
    def __init__(self, session: Session, project_id: str, created_by: str) -> None:
        self.session = session
        self.project_id = project_id
        self.created_by = created_by
        self.project = session.get(Project, project_id)
        if self.project is None:
            raise ValueError("Projeto não encontrado.")
        pin = session.scalar(select(ProjectLibraryPin).where(ProjectLibraryPin.project_id == project_id))
        self.library_version_id = pin.library_version_id if pin else ""
        self.nodes = list(
            session.scalars(select(DocumentNode).where(DocumentNode.project_id == project_id))
        )
        self.nodes_by_id = {n.id: n for n in self.nodes}
        self.display_codes = compute_display_codes(self.nodes)

    def display_code(self, node_id: str) -> str:
        return self.display_codes.get(node_id, "")

    def fascicle_roots(self) -> list[DocumentNode]:
        return [n for n in self.nodes if n.parent_id is None and n.node_type == "fascicle"]

    def subtree_nodes(self, root_id: str) -> list[DocumentNode]:
        result: list[DocumentNode] = []

        def walk(parent_id: str) -> None:
            children = [n for n in self.nodes if n.parent_id == parent_id]
            children.sort(key=lambda n: (n.sort_key, n.id))
            for child in children:
                result.append(child)
                walk(child.id)

        walk(root_id)
        return result

    def blocks_in_fascicle(self, fascicle_id: str) -> list[DocumentNode]:
        return [n for n in self.subtree_nodes(fascicle_id) if n.node_type == "block"]