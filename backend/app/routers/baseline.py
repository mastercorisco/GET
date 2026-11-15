from fastapi import APIRouter, HTTPException

from app.deps import get_settings
from app.schemas.baseline import BaselineResponse
from app.services.baseline_service import BaselineError, get_latest_baseline, publish_baseline
from app.services.workspace_service import WorkspaceError

router = APIRouter(tags=["baseline"])


def _run(action):
    try:
        return action()
    except WorkspaceError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except BaselineError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/projects/{project_id}/baselines/latest", response_model=BaselineResponse | None)
def baseline_latest(project_id: str) -> BaselineResponse | None:
    return _run(lambda: get_latest_baseline(get_settings(), project_id))


@router.post("/projects/{project_id}/baselines/publish", response_model=BaselineResponse)
def baseline_publish(project_id: str) -> BaselineResponse:
    return _run(lambda: publish_baseline(get_settings(), project_id))