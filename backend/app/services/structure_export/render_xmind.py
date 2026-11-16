from __future__ import annotations

import io
import json
import uuid
import zipfile

from app.schemas.structure_export import DocumentStructureSnapshotV1, PointFullSnapshot, StructureTreeNodeSnapshot


def _topic_id() -> str:
    return str(uuid.uuid4())


def _point_title(p) -> str:
    if isinstance(p, PointFullSnapshot):
        return f"{p.order}. {p.title}"
    return f"{p.order}. {p.title} ({p.status})"


def _node_to_topic(node: StructureTreeNodeSnapshot) -> dict:
    title = node.title
    if node.display_code:
        title = f"{node.display_code} — {title}"
    attached: list[dict] = []
    if node.block_model and node.block_model.objective.strip():
        attached.append(
            {
                "id": _topic_id(),
                "title": "Objectivo: " + node.block_model.objective.strip()[:200],
            }
        )
    if node.points:
        for p in node.points:
            attached.append({"id": _topic_id(), "title": _point_title(p)})
    for child in node.children:
        attached.append(_node_to_topic(child))
    topic: dict = {"id": _topic_id(), "title": title}
    if attached:
        topic["children"] = {"attached": attached}
    return topic


def render_xmind(snapshot: DocumentStructureSnapshotV1) -> bytes:
    if snapshot.tree.node_type == "project":
        root_topic = {
            "id": _topic_id(),
            "title": snapshot.project_name,
            "children": {"attached": [_node_to_topic(c) for c in snapshot.tree.children]},
        }
    else:
        root_topic = _node_to_topic(snapshot.tree)

    content = [
        {
            "id": _topic_id(),
            "class": "sheet",
            "title": "Estrutura documental",
            "rootTopic": root_topic,
        }
    ]

    manifest = {"file-entries": {"content.json": {}, "metadata.json": {}}}
    metadata = {"creator": {"name": "GET", "version": "1.0"}}

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False))
        zf.writestr("content.json", json.dumps(content, ensure_ascii=False))
        zf.writestr("metadata.json", json.dumps(metadata, ensure_ascii=False))
    return buf.getvalue()