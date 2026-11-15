from pydantic import BaseModel


class DeletionResponse(BaseModel):
    mode: str
    detail: str | None = None