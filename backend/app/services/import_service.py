from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import delete, func, select

from app.config import AppSettings
from app.models.baseline import Baseline
from app.models.document import DocumentNode
from app.models.imports import (
    ChangeDecision,
    ChangeProposal,
    ImportQuarantineItem,
    ImportRecord,
    ImportStagingItem,
    MergeSession,
)
from app.models.workspace import WorkspaceSettings
from app.schemas.imports import (
    ConsolidateResponse,
    ImportRecordResponse,
    MergeRequest,
    MergeSessionResponse,
    ProposalDecisionRequest,
    ProposalResponse,
    QuarantineItemResponse,
)
from app.services.baseline_service import get_latest_baseline
from app.services.export.context import ExportBuildContext
from app.services.imports.base_loader import BaseLoadError, load_base_package, resolve_export_record
from app.services.imports.consolidate import ConsolidateError, consolidate_merge_session
from app.services.imports.ingest import IngestError, new_import_id, parse_upload_bytes, write_import_file
from app.services.imports.materialize import materialize_current_package
from app.services.imports.merge import build_merge_proposals, new_proposal_id
from app.services.imports.validate import validate_package
from app.services.workspace_exclusivity import workspace_exclusive
from app.services.workspace_service import workspace_session


class ImportError(Exception):
    pass


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _local_user(session) -> str:
    settings = session.scalar(select(WorkspaceSettings).limit(1))
    return settings.local_user_name if settings else "local_user"


def _import_response(session, row: ImportRecord) -> ImportRecordResponse:
    q_count = session.scalar(
        select(func.count()).select_from(ImportQuarantineItem).where(ImportQuarantineItem.import_id == row.id)
    )
    s_count = session.scalar(
        select(func.count()).select_from(ImportStagingItem).where(ImportStagingItem.import_id == row.id)
    )
    return ImportRecordResponse(
        id=row.id,
        project_id=row.project_id,
        source_filename=row.source_filename,
        raw_path=row.raw_path,
        package_type=row.package_type,
        schema_name=row.schema_name,
        schema_version=row.schema_version,
        linked_export_id=row.linked_export_id,
        export_record_id=row.export_record_id,
        status=row.status,
        created_at=row.created_at.isoformat(),
        quarantine_count=int(q_count or 0),
        staging_count=int(s_count or 0),
    )


def list_imports(app_settings: AppSettings, project_id: str) -> list[ImportRecordResponse]:
    with workspace_session(app_settings) as (session, _paths):
        rows = list(
            session.scalars(
                select(ImportRecord)
                .where(ImportRecord.project_id == project_id)
                .order_by(ImportRecord.created_at.desc())
            )
        )
        return [_import_response(session, row) for row in rows]


def upload_import(
    app_settings: AppSettings,
    project_id: str,
    filename: str,
    raw: bytes,
) -> ImportRecordResponse:
    try:
        pkg = parse_upload_bytes(raw)
        staged, quarantine = validate_package(pkg)
    except IngestError as exc:
        raise ImportError(str(exc)) from exc

    with workspace_exclusive("import_upload"):
        with workspace_session(app_settings, begin_immediate=True) as (session, paths):
            import_id = new_import_id()
            dest = write_import_file(paths.imports_dir, import_id, filename or "import.json", raw)

            export_record = None
            linked_export = pkg.get("export_id")
            if linked_export:
                try:
                    export_record = resolve_export_record(session, project_id, linked_export)
                except BaseLoadError:
                    export_record = None

            record = ImportRecord(
                id=import_id,
                project_id=project_id,
                source_filename=filename or "import.json",
                raw_path=str(dest),
                package_type=pkg.get("package_type", "fascicle_roundtrip"),
                schema_name=pkg.get("schema_name", "get_fascicle_roundtrip"),
                schema_version=pkg.get("schema_version", "0.0.0"),
                linked_export_id=linked_export,
                export_record_id=export_record.id if export_record else None,
                status="staged",
                created_at=_utcnow(),
            )
            session.add(record)
            session.flush()

            for row in staged:
                session.add(
                    ImportStagingItem(
                        id=str(uuid.uuid4()),
                        import_id=import_id,
                        entity_kind=row["entity_kind"],
                        entity_key=row["entity_key"],
                        payload_json=json.dumps(row["payload"], ensure_ascii=False),
                    )
                )
            for row in quarantine:
                session.add(
                    ImportQuarantineItem(
                        id=str(uuid.uuid4()),
                        import_id=import_id,
                        path=row["path"],
                        error_code=row["error_code"],
                        message=row["message"],
                        payload_json=row.get("payload_json"),
                    )
                )
            session.flush()
            return _import_response(session, record)


def list_quarantine(app_settings: AppSettings, import_id: str) -> list[QuarantineItemResponse]:
    with workspace_session(app_settings) as (session, _paths):
        rows = list(
            session.scalars(select(ImportQuarantineItem).where(ImportQuarantineItem.import_id == import_id))
        )
        return [
            QuarantineItemResponse(id=r.id, path=r.path, error_code=r.error_code, message=r.message) for r in rows
        ]


def _proposal_response(proposal: ChangeProposal, decision: ChangeDecision | None) -> ProposalResponse:
    return ProposalResponse(
        id=proposal.id,
        proposal_kind=proposal.proposal_kind,
        target_item_id=proposal.target_item_id,
        title=proposal.title,
        field_changes=json.loads(proposal.field_changes_json),
        conflict=proposal.conflict,
        protected_touch=proposal.protected_touch,
        decision=decision.decision if decision else None,
        destination=decision.destination if decision else None,
        confirmed_protected=decision.confirmed_protected if decision else False,
    )


def _merge_to_response(session, merge: MergeSession) -> MergeSessionResponse:
    pairs = session.execute(
        select(ChangeProposal, ChangeDecision)
        .outerjoin(ChangeDecision, ChangeDecision.proposal_id == ChangeProposal.id)
        .where(ChangeProposal.merge_session_id == merge.id)
        .order_by(ChangeProposal.title)
    ).all()
    return MergeSessionResponse(
        id=merge.id,
        import_id=merge.import_id,
        project_id=merge.project_id,
        base_export_id=merge.base_export_id,
        baseline_id=merge.baseline_id,
        fascicle_node_id=merge.fascicle_node_id,
        status=merge.status,
        summary=json.loads(merge.summary_json),
        proposals=[_proposal_response(p, d) for p, d in pairs],
    )


def run_merge(app_settings: AppSettings, project_id: str, import_id: str, body: MergeRequest) -> MergeSessionResponse:
    latest = get_latest_baseline(app_settings, project_id)
    if latest is None:
        raise ImportError("Publicar baseline antes de analisar importação.")

    with workspace_exclusive("import_merge"):
        with workspace_session(app_settings, begin_immediate=True) as (session, _paths):
            import_row = session.get(ImportRecord, import_id)
            if import_row is None or import_row.project_id != project_id:
                raise ImportError("Importação não encontrada.")
            fascicle = session.get(DocumentNode, body.fascicle_node_id)
            if fascicle is None or fascicle.project_id != project_id:
                raise ImportError("Fascículo inválido.")

            pkg = json.loads(Path(import_row.raw_path).read_text(encoding="utf-8"))
            export_id = pkg.get("export_id")
            if not export_id:
                raise ImportError("Pacote sem export_id.")
            try:
                export_record = resolve_export_record(session, project_id, export_id)
            except BaseLoadError as exc:
                raise ImportError(str(exc)) from exc
            base_pkg = load_base_package(export_record)
            if base_pkg.get("fascicle", {}).get("id") != fascicle.id:
                raise ImportError("Fascículo do pacote não coincide com o seleccionado.")

            baseline = session.get(Baseline, latest.id)
            if baseline is None:
                raise ImportError("Baseline não encontrada.")
            ctx = ExportBuildContext(session, project_id, baseline, _local_user(session))
            profile = pkg.get("export_profile", "discussion")
            current_pkg = materialize_current_package(ctx, fascicle, profile, export_id)
            proposals, summary = build_merge_proposals(base_pkg, current_pkg, pkg)

            old_merges = list(session.scalars(select(MergeSession).where(MergeSession.import_id == import_id)))
            for old in old_merges:
                props = list(
                    session.scalars(select(ChangeProposal).where(ChangeProposal.merge_session_id == old.id))
                )
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
                fascicle_node_id=fascicle.id,
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
            return _merge_to_response(session, merge)


def get_latest_merge(app_settings: AppSettings, project_id: str, import_id: str) -> MergeSessionResponse | None:
    with workspace_session(app_settings) as (session, _paths):
        import_row = session.get(ImportRecord, import_id)
        if import_row is None or import_row.project_id != project_id:
            raise ImportError("Importação não encontrada.")
        merge = session.scalar(
            select(MergeSession)
            .where(MergeSession.import_id == import_id)
            .order_by(MergeSession.created_at.desc())
            .limit(1)
        )
        if merge is None:
            return None
        return _merge_to_response(session, merge)


def decide_proposal(
    app_settings: AppSettings,
    merge_session_id: str,
    proposal_id: str,
    body: ProposalDecisionRequest,
) -> ProposalResponse:
    with workspace_session(app_settings) as (session, _paths):
        proposal = session.get(ChangeProposal, proposal_id)
        if proposal is None or proposal.merge_session_id != merge_session_id:
            raise ImportError("Proposta não encontrada.")
        decision = session.scalar(select(ChangeDecision).where(ChangeDecision.proposal_id == proposal_id))
        if decision is None:
            raise ImportError("Decisão não encontrada.")
        decision.decision = body.decision
        decision.destination = body.destination
        decision.confirmed_protected = body.confirmed_protected
        decision.decided_at = _utcnow()
        session.flush()
        return _proposal_response(proposal, decision)


def consolidate(app_settings: AppSettings, merge_session_id: str) -> ConsolidateResponse:
    try:
        backup_id = consolidate_merge_session(app_settings, merge_session_id)
    except ConsolidateError as exc:
        raise ImportError(str(exc)) from exc
    with workspace_session(app_settings) as (session, _paths):
        merge = session.get(MergeSession, merge_session_id)
        if merge is None:
            raise ImportError("Sessão de merge não encontrada.")
        import_row = session.get(ImportRecord, merge.import_id)
        return ConsolidateResponse(
            merge_session_id=merge_session_id,
            backup_id=backup_id,
            import_status=import_row.status if import_row else "unknown",
        )