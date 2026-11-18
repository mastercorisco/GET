from fastapi import APIRouter, File, HTTPException, UploadFile

from app.deps import get_settings
from app.schemas.imports import (
    ConsolidateResponse,
    ImportRecordResponse,
    MergeRequest,
    MergeSessionResponse,
    ProposalDecisionRequest,
    ProposalResponse,
    QuarantineItemResponse,
)
from app.services.import_service import (
    ImportError,
    consolidate,
    decide_proposal,
    get_latest_merge,
    list_imports,
    list_quarantine,
    run_merge,
    upload_import,
)
from app.services.workspace_exclusivity import WorkspaceExclusiveError
from app.services.workspace_service import WorkspaceError

router = APIRouter(tags=["import"])


def _run(action):
    try:
        return action()
    except (WorkspaceError, WorkspaceExclusiveError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ImportError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/projects/{project_id}/imports", response_model=list[ImportRecordResponse])
def imports_list(project_id: str) -> list[ImportRecordResponse]:
    return _run(lambda: list_imports(get_settings(), project_id))


@router.post("/projects/{project_id}/imports", response_model=ImportRecordResponse)
async def imports_upload(project_id: str, file: UploadFile = File(...)) -> ImportRecordResponse:
    raw = await file.read()
    filename = file.filename or "import.json"
    return _run(lambda: upload_import(get_settings(), project_id, filename, raw))


@router.get("/projects/{project_id}/imports/{import_id}/quarantine", response_model=list[QuarantineItemResponse])
def imports_quarantine(project_id: str, import_id: str) -> list[QuarantineItemResponse]:
    return _run(lambda: list_quarantine(get_settings(), import_id))


@router.post("/projects/{project_id}/imports/{import_id}/merge", response_model=MergeSessionResponse)
def imports_merge(project_id: str, import_id: str, body: MergeRequest) -> MergeSessionResponse:
    return _run(lambda: run_merge(get_settings(), project_id, import_id, body))


@router.get(
    "/projects/{project_id}/imports/{import_id}/merge/latest",
    response_model=MergeSessionResponse | None,
)
def imports_merge_latest(project_id: str, import_id: str) -> MergeSessionResponse | None:
    return _run(lambda: get_latest_merge(get_settings(), project_id, import_id))


@router.patch(
    "/projects/{project_id}/imports/merge/{merge_session_id}/proposals/{proposal_id}",
    response_model=ProposalResponse,
)
def imports_proposal_decide(
    project_id: str, merge_session_id: str, proposal_id: str, body: ProposalDecisionRequest
) -> ProposalResponse:
    return _run(lambda: decide_proposal(get_settings(), merge_session_id, proposal_id, body))


@router.post(
    "/projects/{project_id}/imports/merge/{merge_session_id}/consolidate",
    response_model=ConsolidateResponse,
)
def imports_consolidate(project_id: str, merge_session_id: str) -> ConsolidateResponse:
    return _run(lambda: consolidate(get_settings(), merge_session_id))