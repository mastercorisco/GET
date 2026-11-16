from __future__ import annotations

import json
from typing import Any

from app.models.project import Project
from app.schemas.project import ProjectLlmContext


def parse_llm_context(raw: str) -> ProjectLlmContext:
    try:
        data = json.loads(raw or "{}")
    except json.JSONDecodeError:
        data = {}
    if not isinstance(data, dict):
        data = {}
    return ProjectLlmContext.model_validate(data)


def build_project_payload(project: Project) -> dict[str, Any]:
    llm_ctx = parse_llm_context(project.llm_context_json)
    payload: dict[str, Any] = {
        "id": project.id,
        "name": project.name,
        "intervention_type": project.intervention_type,
    }
    if llm_ctx.code:
        payload["code"] = llm_ctx.code
    if llm_ctx.owner:
        payload["owner"] = llm_ctx.owner
    if llm_ctx.location is not None:
        payload["location"] = llm_ctx.location.model_dump(exclude_none=True)
    if llm_ctx.project_type:
        payload["project_type"] = llm_ctx.project_type
    if llm_ctx.document_type:
        payload["document_type"] = llm_ctx.document_type
    return payload