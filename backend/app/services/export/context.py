from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.baseline import Baseline, BaselineDocumentCode, BaselineEntry
from app.models.document import DocumentAssociation, DocumentNode
from app.models.knowledge import KnowledgeItem
from app.models.project import Project, ProjectLibraryPin
from app.models.technical import TechnicalInstance


class ExportBuildContext:
    def __init__(self, session: Session, project_id: str, baseline: Baseline, created_by: str) -> None:
        self.session = session
        self.project_id = project_id
        self.baseline = baseline
        self.created_by = created_by
        self.project = session.get(Project, project_id)
        assert self.project is not None
        pin = session.scalar(select(ProjectLibraryPin).where(ProjectLibraryPin.project_id == project_id))
        self.library_version_id = pin.library_version_id if pin else ""

        self._codes = {
            row.document_node_id: row.display_code
            for row in session.scalars(
                select(BaselineDocumentCode).where(BaselineDocumentCode.baseline_id == baseline.id)
            )
        }
        self._entries = {
            row.entity_id: row.revision_num
            for row in session.scalars(
                select(BaselineEntry).where(
                    BaselineEntry.baseline_id == baseline.id,
                    BaselineEntry.entity_type == "knowledge_item",
                )
            )
        }
        self.nodes = list(
            session.scalars(select(DocumentNode).where(DocumentNode.project_id == project_id))
        )
        self.nodes_by_id = {n.id: n for n in self.nodes}

    def frozen_code(self, node_id: str) -> str:
        return self._codes.get(node_id, "UNK")

    def project_knowledge_items(self) -> list[KnowledgeItem]:
        return list(
            self.session.scalars(
                select(KnowledgeItem).where(
                    KnowledgeItem.scope_type == "project",
                    KnowledgeItem.scope_id == self.project_id,
                )
            )
        )

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

    def associations_for(self, node_id: str) -> list[DocumentAssociation]:
        return list(
            self.session.scalars(
                select(DocumentAssociation).where(DocumentAssociation.document_node_id == node_id)
            )
        )

    def technical_instances(self) -> list[TechnicalInstance]:
        return list(
            self.session.scalars(
                select(TechnicalInstance).where(TechnicalInstance.project_id == self.project_id)
            )
        )