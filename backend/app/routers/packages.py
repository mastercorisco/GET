from fastapi import APIRouter, File, HTTPException, UploadFile

from app.deps import get_settings
from app.schemas.imports import ConsolidateResponse, MergeSessionResponse, ProposalDecisionRequest, ProposalResponse
from app.schemas.packages import (
    PackageBriefContributionTemplateResponse,
    PackageExportRequest,
    PackageExportResponse,
    PackageImportResponse,
)
from app.services.packages.package_guidance import USER_CONTRIBUTION_TEMPLATE
from app.services.import_service import ImportError, decide_proposal
from app.services.imports.consolidate import ConsolidateError
from app.services.package_service import (
    PackageError,
    consolidate_package,
    export_package,
    import_package,
    merge_response,
    run_package_merge,
)
from app.services.workspace_exclusivity import WorkspaceExclusiveError
from app.services.workspace_service import WorkspaceError

router = APIRouter(tags=["packages"])


@router.get("/packages/brief-contribution-template", response_model=PackageBriefContributionTemplateResponse)
def packages_brief_contribution_template() -> PackageBriefContributionTemplateResponse:
    return PackageBriefContributionTemplateResponse(template=USER_CONTRIBUTION_TEMPLATE.strip())


def _run(action):
    try:
        return action()
    except (WorkspaceError, WorkspaceExclusiveError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except (PackageError, ImportError, ConsolidateError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/projects/{project_id}/packages/export", response_model=PackageExportResponse)
def packages_export(project_id: str, body: PackageExportRequest) -> PackageExportResponse:
    return _run(lambda: export_package(get_settings(), project_id, body))


@router.post("/projects/{project_id}/packages/import", response_model=PackageImportResponse)
async def packages_import(project_id: str, file: UploadFile = File(...)) -> PackageImportResponse:
    raw = await file.read()
    filename = file.filename or "package.json"
    return _run(lambda: import_package(get_settings(), project_id, filename, raw))


@router.post("/projects/{project_id}/packages/imports/{import_id}/merge", response_model=MergeSessionResponse)
def packages_merge(project_id: str, import_id: str) -> MergeSessionResponse:
    def action():
        merge_id = run_package_merge(get_settings(), project_id, import_id)
        return merge_response(get_settings(), merge_id)

    return _run(action)


@router.patch(
    "/projects/{project_id}/packages/merge/{merge_session_id}/proposals/{proposal_id}",
    response_model=ProposalResponse,
)
def packages_proposal_decide(
    project_id: str,
    merge_session_id: str,
    proposal_id: str,
    body: ProposalDecisionRequest,
) -> ProposalResponse:
    return _run(lambda: decide_proposal(get_settings(), merge_session_id, proposal_id, body))


@router.post(
    "/projects/{project_id}/packages/merge/{merge_session_id}/consolidate",
    response_model=ConsolidateResponse,
)
def packages_consolidate(project_id: str, merge_session_id: str) -> ConsolidateResponse:
    def action():
        backup_id = consolidate_package(get_settings(), merge_session_id)
        return ConsolidateResponse(merge_session_id=merge_session_id, backup_id=backup_id, import_status="consolidated")

    return _run(action)