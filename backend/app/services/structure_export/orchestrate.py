from __future__ import annotations

import re
import uuid
from pathlib import Path

from app.config import AppSettings
from app.schemas.structure_export import StructureExportRequest, StructureExportResponseMeta
from app.services.structure_export.collect import StructureExportError, collect_snapshot
from app.services.structure_export.render_docx import render_docx
from app.services.structure_export.render_markdown import render_markdown
from app.services.structure_export.render_pdf import render_pdf
from app.services.structure_export.render_xmind import render_xmind
from app.services.structure_export.render_xlsx import render_xlsx
from app.services.workspace_service import WorkspaceError, workspace_session

_MEDIA = {
    "markdown": ("text/markdown; charset=utf-8", "md"),
    "pdf": ("application/pdf", "pdf"),
    "xmind": ("application/vnd.xmind.workbook", "xmind"),
    "docx": (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "docx",
    ),
    "xlsx": (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "xlsx",
    ),
}


def _safe_slug(name: str) -> str:
    slug = re.sub(r"[^\w\-]+", "_", name.strip(), flags=re.UNICODE)
    return slug[:80] or "projecto"


def export_document_structure(
    app_settings: AppSettings,
    project_id: str,
    request: StructureExportRequest,
) -> tuple[bytes, str, str, StructureExportResponseMeta]:
    if request.point_detail != "full" and request.include_point_premises:
        raise StructureExportError("Premissas de ponto só disponíveis com point_detail=full.")

    try:
        with workspace_session(app_settings) as (session, paths):
            paths.ensure_layout()
            snapshot = collect_snapshot(session, project_id, request)
            if request.format == "markdown":
                payload = render_markdown(snapshot).encode("utf-8")
            elif request.format == "pdf":
                payload = render_pdf(snapshot)
            elif request.format == "xmind":
                payload = render_xmind(snapshot)
            elif request.format == "docx":
                payload = render_docx(snapshot)
            else:
                payload = render_xlsx(snapshot)

            media_type, ext = _MEDIA[request.format]
            run_id = str(uuid.uuid4())
            out_dir = paths.exports_dir / "document-structure" / run_id
            out_dir.mkdir(parents=True, exist_ok=True)
            code = snapshot.root_display_code or "PROJECT"
            file_name = f"estrutura_{_safe_slug(code)}_{run_id[:8]}.{ext}"
            file_path = out_dir / file_name
            file_path.write_bytes(payload)
            rel = str(file_path.relative_to(paths.root)).replace("\\", "/")
            meta = StructureExportResponseMeta(
                file_name=file_name,
                relative_path=rel,
                format=request.format,
                byte_size=len(payload),
                run_id=run_id,
            )
            return payload, file_name, media_type, meta
    except WorkspaceError as exc:
        raise StructureExportError(str(exc)) from exc