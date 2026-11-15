from pydantic import BaseModel, Field


class WorkspaceCreateRequest(BaseModel):
    root_path: str = Field(min_length=1)
    local_user_name: str = Field(min_length=1, default="local_user")


class WorkspaceOpenRequest(BaseModel):
    root_path: str = Field(min_length=1)


class WorkspaceResponse(BaseModel):
    id: str
    root_path: str
    local_user_name: str
    database_path: str
    backups_path: str
    exports_path: str
    imports_path: str