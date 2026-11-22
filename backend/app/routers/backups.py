from fastapi import APIRouter, HTTPException

from app.deps import get_settings
from app.schemas.backup import BackupCreateRequest, BackupRecordResponse, BackupRestorePreviewResponse
from app.services.backup_service import (
    create_backup,
    delete_backup,
    list_backups,
    restore_backup,
    restore_preview,
)
from app.services.workspace_exclusivity import WorkspaceExclusiveError
from app.services.workspace_service import WorkspaceError

router = APIRouter(prefix="/backups", tags=["backups"])


@router.get("", response_model=list[BackupRecordResponse])
def backups_list() -> list[BackupRecordResponse]:
    try:
        return list_backups(get_settings())
    except WorkspaceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("", response_model=BackupRecordResponse)
def backups_create(body: BackupCreateRequest) -> BackupRecordResponse:
    try:
        return create_backup(get_settings(), body.tier, user_note=body.user_note)
    except WorkspaceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{backup_id}/preview", response_model=BackupRestorePreviewResponse)
def backups_preview(backup_id: str) -> BackupRestorePreviewResponse:
    try:
        return restore_preview(get_settings(), backup_id)
    except WorkspaceError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


def _delete_backup_http(backup_id: str) -> None:
    try:
        delete_backup(get_settings(), backup_id)
    except WorkspaceExclusiveError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except WorkspaceError as exc:
        msg = str(exc)
        status = 409 if "bloqueado" in msg.lower() or "em uso" in msg.lower() else 404
        raise HTTPException(status_code=status, detail=msg) from exc


@router.delete("/{backup_id}", status_code=204)
def backups_delete(backup_id: str) -> None:
    _delete_backup_http(backup_id)


@router.post("/{backup_id}/discard", status_code=204)
def backups_discard(backup_id: str) -> None:
    """Apagar registo e ficheiro (POST para compatibilidade com o mesmo padrão que restore)."""
    _delete_backup_http(backup_id)


@router.post("/{backup_id}/restore")
def backups_restore(backup_id: str, confirm: bool = False) -> dict[str, str]:
    try:
        restore_backup(get_settings(), backup_id, confirm=confirm)
        return {"status": "restored", "backup_id": backup_id}
    except WorkspaceExclusiveError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except WorkspaceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc