from pydantic import BaseModel


class BaselineResponse(BaseModel):
    id: str
    project_id: str
    code: str
    revision: int
    library_version_id: str
    created_at: str