from __future__ import annotations

import hashlib
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select

from app.config import AppSettings
from app.models.baseline import Baseline, ExportRecord
from app.models.workspace import WorkspaceSettings
from app.schemas.export import (
    ExportRecordResponse,
    FascicleExportRequest,
    LlmGenerationExportRequest,
    LlmGenerationExportResponse,
    MasterExportRequest,
)
from app.services.llm_export.orchestrate import export_llm_generation_package, local_user
from app.services.baseline_service import get_latest_baseline
from app.services.export.context import ExportBuildContext
from app.services.export.fascicle_builder import build_fascicle_package
from app.services.export.master_builder import build_fascicle_payloads, build_master_package, sha256_hex
from app.services.export.serializer import dumps_deterministic
from app.services.export.validator import validate_fascicle, validate_master
from app.services.workspace_service import workspace_session


class ExportError(Exception):
    pass


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _record_response(row: ExportRecord, zip_path: str | None = None) -> ExportRecordResponse:
    return ExportRecordResponse(
        id=row.id,
        project_id=row.project_id,
        baseline_id=row.baseline_id,
        export_id=row.export_id,
        profile=row.profile,
        schema_name=row.schema_name,
        sha256=row.sha256,
        file_path=row.file_path,
        package_type=row.package_type,
        parent_export_id=row.parent_export_id,
        created_at=row.created_at.isoformat(),
        zip_path=zip_path,
    )


def _local_user(session) -> str:
    settings = session.scalar(select(WorkspaceSettings).limit(1))
    return settings.local_user_name if settings else "local_user"


def _write_markdown(path: Path, fascicle_title: str, display_code: str, item_titles: list[str]) -> None:
    lines = [
        f"# {display_code} — {fascicle_title}",
        "",
        "Documento derivado para leitura. **Não reimportável.**",
        "",
        "## Unidades referenciadas",
    ]
    if not item_titles:
        lines.append("- (nenhuma)")
    else:
        for title in item_titles:
            lines.append(f"- {title}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def list_exports(app_settings: AppSettings, project_id: str) -> list[ExportRecordResponse]:
    with workspace_session(app_settings) as (session, _paths):
        rows = list(
            session.scalars(
                select(ExportRecord)
                .where(ExportRecord.project_id == project_id)
                .order_by(ExportRecord.created_at.desc())
            )
        )
        return [_record_response(row) for row in rows]


def export_master(app_settings: AppSettings, project_id: str, body: MasterExportRequest) -> ExportRecordResponse:
    latest = get_latest_baseline(app_settings, project_id)
    if latest is None:
        raise ExportError("Publicar baseline antes de exportar.")

    warnings: list[dict] = []
    errors: list[dict] = []

    with workspace_session(app_settings) as (session, paths):
        baseline = session.get(Baseline, latest.id)
        if baseline is None:
            raise ExportError("Baseline não encontrada.")
        ctx = ExportBuildContext(session, project_id, baseline, _local_user(session))
        export_id = f"EXP-MASTER-{baseline.code}"
        out_dir = paths.exports_dir / export_id
        out_dir.mkdir(parents=True, exist_ok=True)

        fascicle_payloads = build_fascicle_payloads(
            ctx,
            profile=body.profile,
            export_id_prefix=export_id,
            warnings=warnings,
            errors=errors,
        )
        fascicle_hashes: dict[str, str] = {}
        zip_targets: list[Path] = []

        for fascicle_id, payload in fascicle_payloads.items():
            fascicle_errors = validate_fascicle(payload)
            if fascicle_errors:
                errors.extend([{"code": "SCHEMA", "message": msg} for msg in fascicle_errors[:5]])
            text = dumps_deterministic(payload)
            code = ctx.frozen_code(fascicle_id)
            filename = f"{code}_{body.profile}.json"
            file_path = out_dir / filename
            file_path.write_text(text, encoding="utf-8")
            fascicle_hashes[fascicle_id] = sha256_hex(text)
            zip_targets.append(file_path)

            titles = [
                *(i["title"] for i in payload["protected_context"].get("knowledge_items", [])),
                *(i["title"] for i in payload["editable_knowledge"].get("knowledge_items", [])),
            ]
            md_path = out_dir / f"{code}_{body.profile}.md"
            _write_markdown(md_path, payload["fascicle"]["title"], code, titles)
            zip_targets.append(md_path)

        master = build_master_package(
            ctx,
            profile=body.profile,
            export_id=export_id,
            fascicle_hashes=fascicle_hashes,
            warnings=warnings,
            errors=errors,
        )
        master_errors = validate_master(master)
        if master_errors:
            errors.extend([{"code": "SCHEMA", "message": msg} for msg in master_errors[:5]])
            master["validation"]["status"] = "invalid"
            master["validation"]["errors"] = errors

        master_text = dumps_deterministic(master)
        master_path = out_dir / f"master_{body.profile}.json"
        master_path.write_text(master_text, encoding="utf-8")
        zip_targets.insert(0, master_path)

        zip_path: str | None = None
        if body.write_zip:
            zip_file = out_dir / "export_package.zip"
            with zipfile.ZipFile(zip_file, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                for target in zip_targets:
                    zf.write(target, arcname=target.name)
                zf.writestr(
                    "validation.json",
                    dumps_deterministic(master["validation"]),
                )
            zip_path = str(zip_file)

        sha = sha256_hex(master_text)
        record = session.scalar(select(ExportRecord).where(ExportRecord.export_id == export_id))
        if record is None:
            record = ExportRecord(
                id=str(uuid.uuid4()),
                project_id=project_id,
                baseline_id=baseline.id,
                export_id=export_id,
                profile=body.profile,
                schema_name="get_project_master",
                sha256=sha,
                file_path=str(master_path),
                package_type="master",
                parent_export_id=None,
                created_at=_utcnow(),
            )
            session.add(record)
        else:
            record.sha256 = sha
            record.file_path = str(master_path)
            record.baseline_id = baseline.id
            record.created_at = _utcnow()
        session.flush()
        return _record_response(record, zip_path=zip_path)


def export_fascicle(
    app_settings: AppSettings,
    project_id: str,
    fascicle_node_id: str,
    body: FascicleExportRequest,
) -> ExportRecordResponse:
    latest = get_latest_baseline(app_settings, project_id)
    if latest is None:
        raise ExportError("Publicar baseline antes de exportar.")

    warnings: list[dict] = []
    errors: list[dict] = []

    with workspace_session(app_settings) as (session, paths):
        baseline = session.get(Baseline, latest.id)
        if baseline is None:
            raise ExportError("Baseline não encontrada.")
        ctx = ExportBuildContext(session, project_id, baseline, _local_user(session))
        fascicle = ctx.nodes_by_id.get(fascicle_node_id)
        if fascicle is None or fascicle.node_type != "fascicle":
            raise ExportError("Nó fascículo inválido.")

        code = ctx.frozen_code(fascicle.id)
        export_id = f"EXP-FASC-{code}"
        out_dir = paths.exports_dir / export_id
        out_dir.mkdir(parents=True, exist_ok=True)

        payload = build_fascicle_package(
            ctx,
            fascicle,
            profile=body.profile,
            export_id=export_id,
            warnings=warnings,
            errors=errors,
        )
        fascicle_errors = validate_fascicle(payload)
        if fascicle_errors:
            errors.extend([{"code": "SCHEMA", "message": msg} for msg in fascicle_errors[:10]])
            payload["validation"]["status"] = "invalid"
            payload["validation"]["errors"] = errors

        text = dumps_deterministic(payload)
        json_path = out_dir / f"{code}_{body.profile}.json"
        json_path.write_text(text, encoding="utf-8")

        titles = [
            *(i["title"] for i in payload["protected_context"].get("knowledge_items", [])),
            *(i["title"] for i in payload["editable_knowledge"].get("knowledge_items", [])),
        ]
        md_path = out_dir / f"{code}_{body.profile}.md"
        _write_markdown(md_path, fascicle.title, code, titles)

        zip_path: str | None = None
        if body.write_zip:
            zip_file = out_dir / "export_package.zip"
            with zipfile.ZipFile(zip_file, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                zf.write(json_path, arcname=json_path.name)
                zf.write(md_path, arcname=md_path.name)
                zf.writestr("validation.json", dumps_deterministic(payload["validation"]))
            zip_path = str(zip_file)

        parent_id = None
        if body.master_export_id:
            parent = session.scalar(
                select(ExportRecord).where(ExportRecord.export_id == body.master_export_id)
            )
            parent_id = parent.id if parent else None

        sha = sha256_hex(text)
        record = session.scalar(select(ExportRecord).where(ExportRecord.export_id == export_id))
        if record is None:
            record = ExportRecord(
                id=str(uuid.uuid4()),
                project_id=project_id,
                baseline_id=baseline.id,
                export_id=export_id,
                profile=body.profile,
                schema_name="get_fascicle_roundtrip",
                sha256=sha,
                file_path=str(json_path),
                package_type="fascicle_roundtrip",
                parent_export_id=parent_id,
                created_at=_utcnow(),
            )
            session.add(record)
        else:
            record.sha256 = sha
            record.file_path = str(json_path)
            record.baseline_id = baseline.id
            record.parent_export_id = parent_id
            record.created_at = _utcnow()
        session.flush()
        return _record_response(record, zip_path=zip_path)


def export_llm_generation(
    app_settings: AppSettings,
    project_id: str,
    body: LlmGenerationExportRequest,
) -> LlmGenerationExportResponse:
    with workspace_session(app_settings) as (session, paths):
        latest = get_latest_baseline(app_settings, project_id)
        baseline_id = latest.id if latest is not None else None
        try:
            result = export_llm_generation_package(
                session,
                paths,
                project_id,
                profile=body.profile,
                include_draft=body.include_draft,
                fascicle_node_id=body.fascicle_node_id,
                created_by=local_user(session),
                baseline_id=baseline_id,
            )
        except ValueError as exc:
            raise ExportError(str(exc)) from exc
        return LlmGenerationExportResponse(
            export_id=result.export_id,
            file_path=result.master_path,
            zip_path=result.zip_path,
            sha256=result.sha256,
            manifest=result.manifest,
        )