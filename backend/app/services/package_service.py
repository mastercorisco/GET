from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import delete, select

from app.config import AppSettings
from app.models.baseline import Baseline, ExportRecord
from app.models.document import DocumentNode
from app.models.imports import ChangeDecision, ChangeProposal, ImportRecord, MergeSession
from app.models.workspace import WorkspaceSettings
from app.schemas.packages import (
    PackageExportRequest,
    PackageExportResponse,
    PackageImportResponse,
)
from app.services.baseline_service import get_latest_baseline
from app.services.export.context import ExportBuildContext
from app.services.export.fascicle_builder import build_fascicle_package
from app.services.export.master_builder import sha256_hex
from app.services.export.serializer import dumps_deterministic
from app.services.imports.base_loader import BaseLoadError, load_base_package, resolve_export_record
from app.services.imports.consolidate import ConsolidateError, _consolidate_in_session
from app.services.imports.ingest import IngestError, new_import_id, parse_upload_bytes, write_import_file
from app.services.imports.materialize import materialize_current_package
from app.services.imports.merge import build_merge_proposals, new_proposal_id
from app.services.packages.block_builder import build_block_payload
from app.services.packages.block_consolidate import apply_block_proposals
from app.services.packages.block_merge import build_block_merge_proposals
from app.services.packages.envelope import unwrap_block_payload, unwrap_fascicle_payload, wrap_package
from app.services.packages.validate_strict import PackageValidationError, validate_get_package
from app.services.workspace_service import workspace_session


class PackageError(Exception):
    pass


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _local_user(session) -> str:
    settings = session.scalar(select(WorkspaceSettings).limit(1))
    return settings.local_user_name if settings else "local_user"


def export_package(
    app_settings: AppSettings,
    project_id: str,
    body: PackageExportRequest,
) -> PackageExportResponse:
    latest = get_latest_baseline(app_settings, project_id)
    if latest is None:
        raise PackageError("Publicar baseline antes de exportar pacote.")

    profile = body.profile or "discussion"

    with workspace_session(app_settings) as (session, paths):
        baseline = session.get(Baseline, latest.id)
        if baseline is None:
            raise PackageError("Baseline não encontrada.")

        if body.scope_kind == "fascicle":
            fascicle = session.get(DocumentNode, body.node_id)
            if fascicle is None or fascicle.node_type != "fascicle" or fascicle.project_id != project_id:
                raise PackageError("Fascículo inválido.")
            ctx = ExportBuildContext(session, project_id, baseline, _local_user(session))
            code = ctx.frozen_code(fascicle.id)
            export_id = f"PKG-FASC-{code}"
            warnings: list[dict] = []
            errors: list[dict] = []
            inner = build_fascicle_package(
                ctx,
                fascicle,
                profile=profile,
                export_id=export_id,
                warnings=warnings,
                errors=errors,
            )
            pkg = wrap_package(
                scope_kind="fascicle",
                project_id=project_id,
                fascicle_id=fascicle.id,
                block_id=None,
                export_id=export_id,
                payload=inner,
            )
            out_dir = paths.exports_dir / export_id
            out_dir.mkdir(parents=True, exist_ok=True)
            filename = f"{code}_package.json"
        elif body.scope_kind == "block":
            block = session.get(DocumentNode, body.node_id)
            if block is None or block.node_type != "block" or block.project_id != project_id:
                raise PackageError("Bloco inválido.")
            codes_ctx_nodes = list(
                session.scalars(select(DocumentNode).where(DocumentNode.project_id == project_id))
            )
            from app.services.document_service import compute_display_codes

            codes = compute_display_codes(codes_ctx_nodes)
            code = codes.get(block.id, block.id[:8])
            export_id = f"PKG-BLK-{code}"
            inner = build_block_payload(session, block.id)
            pkg = wrap_package(
                scope_kind="block",
                project_id=project_id,
                fascicle_id=None,
                block_id=block.id,
                export_id=export_id,
                payload=inner,
            )
            out_dir = paths.exports_dir / export_id
            out_dir.mkdir(parents=True, exist_ok=True)
            filename = f"{code}_package.json"
        else:
            raise PackageError("Âmbito inválido.")

        text = dumps_deterministic(pkg)
        json_path = out_dir / filename
        json_path.write_text(text, encoding="utf-8")
        sha = sha256_hex(text)

        record = session.scalar(select(ExportRecord).where(ExportRecord.export_id == export_id))
        if record is None:
            record = ExportRecord(
                id=str(uuid.uuid4()),
                project_id=project_id,
                baseline_id=baseline.id,
                export_id=export_id,
                profile=profile,
                schema_name="GET-PACKAGE",
                sha256=sha,
                file_path=str(json_path),
                package_type=f"get_package_{body.scope_kind}",
                parent_export_id=None,
                created_at=_utcnow(),
            )
            session.add(record)
        else:
            record.sha256 = sha
            record.file_path = str(json_path)
            record.baseline_id = baseline.id
            record.created_at = _utcnow()

        session.flush()
        return PackageExportResponse(
            export_id=export_id,
            file_path=str(json_path),
            scope_kind=body.scope_kind,
            sha256=sha,
            filename=filename,
            body=text,
        )


def import_package(
    app_settings: AppSettings,
    project_id: str,
    filename: str,
    raw: bytes,
) -> PackageImportResponse:
    try:
        pkg = parse_upload_bytes(raw)
        validate_get_package(pkg, project_id=project_id)
    except IngestError as exc:
        raise PackageError(str(exc)) from exc
    except PackageValidationError as exc:
        raise PackageError(str(exc)) from exc

    scope = pkg.get("scope") or {}
    scope_kind = scope.get("kind", "")

    with workspace_session(app_settings) as (session, paths):
        import_id = new_import_id()
        dest = write_import_file(paths.imports_dir, import_id, filename or "package.json", raw)
        export_id = pkg.get("export_id")

        export_record = None
        if export_id:
            try:
                export_record = resolve_export_record(session, project_id, export_id)
            except BaseLoadError:
                export_record = None

        record = ImportRecord(
            id=import_id,
            project_id=project_id,
            source_filename=filename or "package.json",
            raw_path=str(dest),
            package_type=f"get_package_{scope_kind}",
            schema_name="GET-PACKAGE",
            schema_version=pkg.get("schema_version", "1.0.0"),
            linked_export_id=export_id,
            export_record_id=export_record.id if export_record else None,
            status="staged",
            created_at=_utcnow(),
        )
        session.add(record)
        session.flush()
        return PackageImportResponse(
            import_id=import_id,
            scope_kind=scope_kind,
            export_id=export_id,
            status="staged",
        )


def run_package_merge(app_settings: AppSettings, project_id: str, import_id: str) -> str:
    from app.services.import_service import _local_user as import_local_user

    latest = get_latest_baseline(app_settings, project_id)
    if latest is None:
        raise PackageError("Publicar baseline antes de analisar alterações.")

    with workspace_session(app_settings) as (session, _paths):
        import_row = session.get(ImportRecord, import_id)
        if import_row is None or import_row.project_id != project_id:
            raise PackageError("Importação não encontrada.")
        if not import_row.package_type.startswith("get_package_"):
            raise PackageError("Importação não é um pacote GET-PACKAGE.")

        pkg = json.loads(Path(import_row.raw_path).read_text(encoding="utf-8"))
        validate_get_package(pkg, project_id=project_id)
        scope = pkg.get("scope") or {}
        scope_kind = scope.get("kind")
        export_id = pkg.get("export_id")
        if not export_id:
            raise PackageError("Pacote sem export_id.")

        try:
            export_record = resolve_export_record(session, project_id, export_id)
        except BaseLoadError as exc:
            raise PackageError(str(exc)) from exc

        baseline = session.get(Baseline, latest.id)
        if baseline is None:
            raise PackageError("Baseline não encontrada.")

        if scope_kind == "fascicle":
            fascicle_id = scope.get("fascicle_id")
            fascicle = session.get(DocumentNode, fascicle_id)
            if fascicle is None or fascicle.project_id != project_id:
                raise PackageError("Fascículo inválido.")
            base_pkg = unwrap_fascicle_payload(
                json.loads(Path(export_record.file_path).read_text(encoding="utf-8"))
            )
            ctx = ExportBuildContext(session, project_id, baseline, import_local_user(session))
            profile = base_pkg.get("export_profile", "discussion")
            current_pkg = materialize_current_package(ctx, fascicle, profile, export_id)
            returned_pkg = unwrap_fascicle_payload(pkg)
            proposals, summary = build_merge_proposals(base_pkg, current_pkg, returned_pkg)
            merge_node_id = fascicle.id
        elif scope_kind == "block":
            block_id = scope.get("block_id")
            block = session.get(DocumentNode, block_id)
            if block is None or block.project_id != project_id:
                raise PackageError("Bloco inválido.")
            base_raw = json.loads(Path(export_record.file_path).read_text(encoding="utf-8"))
            base_block = unwrap_block_payload(base_raw)
            current_block = build_block_payload(session, block.id)
            returned_block = unwrap_block_payload(pkg)
            proposals, summary = build_block_merge_proposals(base_block, current_block, returned_block)
            merge_node_id = block.id
        else:
            raise PackageError("Âmbito inválido.")

        old_merges = list(session.scalars(select(MergeSession).where(MergeSession.import_id == import_id)))
        for old in old_merges:
            props = list(session.scalars(select(ChangeProposal).where(ChangeProposal.merge_session_id == old.id)))
            for prop in props:
                session.execute(delete(ChangeDecision).where(ChangeDecision.proposal_id == prop.id))
            session.execute(delete(ChangeProposal).where(ChangeProposal.merge_session_id == old.id))
        session.execute(delete(MergeSession).where(MergeSession.import_id == import_id))

        merge_id = str(uuid.uuid4())
        merge = MergeSession(
            id=merge_id,
            import_id=import_id,
            project_id=project_id,
            base_export_id=export_id,
            baseline_id=baseline.id,
            fascicle_node_id=merge_node_id,
            status="open",
            summary_json=json.dumps(summary, ensure_ascii=False),
            created_at=_utcnow(),
        )
        session.add(merge)
        session.flush()

        for item in proposals:
            proposal_id = new_proposal_id()
            session.add(
                ChangeProposal(
                    id=proposal_id,
                    merge_session_id=merge_id,
                    proposal_kind=item["proposal_kind"],
                    target_item_id=item["target_item_id"],
                    title=item["title"],
                    field_changes_json=json.dumps(item["field_changes"], ensure_ascii=False),
                    conflict=item["conflict"],
                    protected_touch=item["protected_touch"],
                )
            )
            session.flush()
            session.add(
                ChangeDecision(
                    id=str(uuid.uuid4()),
                    proposal_id=proposal_id,
                    decision=None,
                    destination=None,
                    confirmed_protected=False,
                    decided_at=None,
                )
            )
        import_row.status = "merged"
        session.flush()
        return merge_id


def consolidate_package(app_settings: AppSettings, merge_session_id: str) -> str:
    from app.services.backup_service import create_backup

    backup = create_backup(app_settings, "critical")
    with workspace_session(app_settings) as (session, _paths):
        merge = session.get(MergeSession, merge_session_id)
        if merge is None:
            raise ConsolidateError("Sessão de merge não encontrada.")
        import_row = session.get(ImportRecord, merge.import_id)
        if import_row and import_row.package_type == "get_package_block":
            apply_block_proposals(session, merge_session_id)
            merge.status = "consolidated"
            import_row.status = "consolidated"
        else:
            _consolidate_in_session(session, merge_session_id)
        return backup.id


def merge_response(app_settings: AppSettings, merge_session_id: str):
    from app.services.import_service import _merge_to_response

    with workspace_session(app_settings) as (session, _paths):
        merge = session.get(MergeSession, merge_session_id)
        if merge is None:
            raise PackageError("Sessão de merge não encontrada.")
        return _merge_to_response(session, merge)