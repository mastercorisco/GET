from __future__ import annotations

import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.baseline import ExportRecord
from app.models.workspace import WorkspaceSettings
from app.services.export.master_builder import sha256_hex
from app.services.export.serializer import dumps_deterministic
from app.services.llm_export.block_eligibility import block_has_exportable_points
from app.services.llm_export.build_fascicle_llm import build_fascicle_llm_index
from app.services.llm_export.build_master_llm import build_master_llm
from app.services.llm_export.builder import build_llm_block_export
from app.services.llm_export.live_context import LlmLiveContext
from app.services.llm_export.render_md import render_llm_export_md
from app.services.llm_export.render_terminology_md import render_terminology_glossary_md
from app.services.llm_export.terminology_snapshot import build_terminology_snapshot
from app.services.workspace_service import WorkspacePaths


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _safe_filename(code: str) -> str:
    return "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in code)


class LlmGenerationResult:
    def __init__(
        self,
        *,
        export_id: str,
        master_path: str,
        zip_path: str,
        sha256: str,
        manifest: dict[str, Any],
    ) -> None:
        self.export_id = export_id
        self.master_path = master_path
        self.zip_path = zip_path
        self.sha256 = sha256
        self.manifest = manifest


def export_llm_generation_package(
    session: Session,
    paths: WorkspacePaths,
    project_id: str,
    *,
    profile: str,
    include_draft: bool,
    fascicle_node_id: str | None,
    created_by: str,
    baseline_id: str | None,
) -> LlmGenerationResult:
    ctx = LlmLiveContext(session, project_id, created_by)
    generated_at = _utcnow().isoformat()
    package_export_id = f"EXP-LLM-{project_id[:8]}"
    out_dir = paths.exports_dir / package_export_id
    out_dir.mkdir(parents=True, exist_ok=True)

    fascicles = ctx.fascicle_roots()
    if fascicle_node_id:
        fascicle = ctx.nodes_by_id.get(fascicle_node_id)
        if fascicle is None or fascicle.node_type != "fascicle":
            raise ValueError("Fascículo inválido.")
        fascicles = [fascicle]

    package_files: list[tuple[Path, str]] = []
    fascicle_manifest_for_master: list[dict[str, Any]] = []

    for fascicle in fascicles:
        f_code = ctx.display_code(fascicle.id)
        block_manifest: list[dict[str, Any]] = []

        for block in ctx.blocks_in_fascicle(fascicle.id):
            if not block_has_exportable_points(session, block.id, include_draft=include_draft):
                continue
            b_code = ctx.display_code(block.id)
            block_payload = build_llm_block_export(
                session,
                block.id,
                include_draft=include_draft,
                profile=profile,
                generated_at=generated_at,
                created_by=created_by,
            )
            block_json_name = f"{_safe_filename(b_code)}_{profile}_llm.json"
            block_md_name = f"{_safe_filename(b_code)}_{profile}_llm.md"
            block_json_path = out_dir / block_json_name
            block_md_path = out_dir / block_md_name
            block_text = dumps_deterministic(block_payload)
            block_json_path.write_text(block_text, encoding="utf-8")
            block_md_path.write_text(render_llm_export_md(block_payload), encoding="utf-8")
            block_hash = sha256_hex(block_text)
            package_files.append((block_json_path, block_json_name))
            package_files.append((block_md_path, block_md_name))
            block_manifest.append(
                {
                    "block_id": block.id,
                    "display_code": b_code,
                    "filename": block_json_name,
                    "markdown_filename": block_md_name,
                    "sha256": block_hash,
                }
            )

        fascicle_payload = build_fascicle_llm_index(
            session,
            ctx,
            fascicle,
            profile=profile,
            include_draft=include_draft,
            generated_at=generated_at,
            block_manifest=block_manifest,
        )
        fascicle_json_name = f"{_safe_filename(f_code)}_{profile}_llm.json"
        fascicle_md_name = f"{_safe_filename(f_code)}_{profile}_llm.md"
        fascicle_json_path = out_dir / fascicle_json_name
        fascicle_md_path = out_dir / fascicle_md_name
        fascicle_text = dumps_deterministic(fascicle_payload)
        fascicle_json_path.write_text(fascicle_text, encoding="utf-8")
        fascicle_md_path.write_text(render_llm_export_md(fascicle_payload), encoding="utf-8")
        fascicle_hash = sha256_hex(fascicle_text)
        package_files.append((fascicle_json_path, fascicle_json_name))
        package_files.append((fascicle_md_path, fascicle_md_name))
        fascicle_manifest_for_master.append(
            {
                "fascicle_id": fascicle.id,
                "display_code": f_code,
                "title": fascicle.title,
                "filename": fascicle_json_name,
                "markdown_filename": fascicle_md_name,
                "sha256": fascicle_hash,
                "block_count": len(block_manifest),
            }
        )

    term_md_name = f"terminology_{profile}_llm.md"
    term_json_name = f"terminology_{profile}_llm.json"
    master_payload = build_master_llm(
        session,
        ctx,
        profile=profile,
        export_id=package_export_id,
        generated_at=generated_at,
        fascicle_manifest=fascicle_manifest_for_master,
    )
    master_payload["package_terminology_markdown"] = term_md_name
    master_payload["package_terminology_json"] = term_json_name

    term_snapshot = build_terminology_snapshot(session, project_id)

    term_md_content = render_terminology_glossary_md(
        term_snapshot,
        export_id=package_export_id,
        profile=profile,
        generated_at=generated_at,
    )
    term_md_path = out_dir / term_md_name
    term_md_path.write_text(term_md_content, encoding="utf-8")
    term_hash = sha256_hex(term_md_content)

    term_json_payload: dict[str, Any] = {
        "get_export": {
            "schema": "GET-LLM-TERMINOLOGY",
            "schema_version": "1.0",
            "export_type": "terminology_glossary",
            "generated_at": generated_at,
            "language": "pt-PT",
        },
        "export_id": package_export_id,
        "profile": profile,
        "payload": term_snapshot,
    }
    term_json_text = dumps_deterministic(term_json_payload)
    term_json_path = out_dir / term_json_name
    term_json_path.write_text(term_json_text, encoding="utf-8")
    term_json_hash = sha256_hex(term_json_text)

    master_json_name = f"master_{profile}_llm.json"
    master_md_name = f"master_{profile}_llm.md"
    master_json_path = out_dir / master_json_name
    master_md_path = out_dir / master_md_name
    master_text = dumps_deterministic(master_payload)
    master_json_path.write_text(master_text, encoding="utf-8")
    master_md_path.write_text(render_llm_export_md(master_payload), encoding="utf-8")
    master_hash = sha256_hex(master_text)

    manifest_files: list[dict[str, Any]] = [
        {"path": master_json_name, "kind": "project_master", "sha256": master_hash},
        {
            "path": term_md_name,
            "kind": "terminology_glossary",
            "sha256": term_hash,
        },
        {
            "path": term_json_name,
            "kind": "terminology_glossary",
            "sha256": term_json_hash,
        },
    ]
    for entry in fascicle_manifest_for_master:
        manifest_files.append(
            {"path": entry["filename"], "kind": "fascicle", "sha256": entry["sha256"]}
        )
    for path, arcname in package_files:
        if arcname.endswith("_llm.json") and "_B" in arcname.upper():
            manifest_files.append(
                {
                    "path": arcname,
                    "kind": "block",
                    "sha256": sha256_hex(path.read_text(encoding="utf-8")),
                }
            )

    package_manifest = {
        "schema": "GET-LLM-PACKAGE",
        "schema_version": "1.0",
        "export_id": package_export_id,
        "profile": profile,
        "generated_at": generated_at,
        "include_draft": include_draft,
        "files": manifest_files,
    }
    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(dumps_deterministic(package_manifest), encoding="utf-8")

    zip_path = out_dir / f"llm_generation_{profile}.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(master_json_path, arcname=master_json_name)
        zf.write(master_md_path, arcname=master_md_name)
        zf.write(term_md_path, arcname=term_md_name)
        zf.write(term_json_path, arcname=term_json_name)
        for file_path, arcname in package_files:
            zf.write(file_path, arcname=arcname)
        zf.writestr("manifest.json", dumps_deterministic(package_manifest))

    if baseline_id:
        record = session.scalar(
            select(ExportRecord).where(
                ExportRecord.project_id == project_id,
                ExportRecord.export_id == package_export_id,
            )
        )
        if record is None:
            record = ExportRecord(
                id=str(uuid.uuid4()),
                project_id=project_id,
                baseline_id=baseline_id,
                export_id=package_export_id,
                profile=profile,
                schema_name="get_llm_generation",
                sha256=master_hash,
                file_path=str(master_json_path),
                package_type="llm_generation",
                parent_export_id=None,
                created_at=_utcnow(),
            )
            session.add(record)
        else:
            record.sha256 = master_hash
            record.file_path = str(master_json_path)
            record.baseline_id = baseline_id
            record.created_at = _utcnow()
        session.flush()

    return LlmGenerationResult(
        export_id=package_export_id,
        master_path=str(master_json_path),
        zip_path=str(zip_path),
        sha256=master_hash,
        manifest=package_manifest,
    )


def local_user(session: Session) -> str:
    settings = session.scalar(select(WorkspaceSettings).limit(1))
    return settings.local_user_name if settings else "local_user"