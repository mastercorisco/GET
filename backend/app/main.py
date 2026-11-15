from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.domain.block.router import router as block_router
from app.routers import (
    backups,
    baseline,
    document,
    export,
    import_review,
    workbook,
    health,
    knowledge,
    projects,
    references,
    technical,
    terminology,
    workspace,
)

_STATIC_DIR = Path(__file__).resolve().parent / "static"
_STATIC_INDEX = _STATIC_DIR / "index.html"

app = FastAPI(title="GET — Gerador de Especificações Funcionais", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:4811",
        "http://localhost:4811",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(workspace.router, prefix="/api")
app.include_router(backups.router, prefix="/api")
app.include_router(knowledge.router, prefix="/api")
app.include_router(projects.router, prefix="/api")
app.include_router(technical.router, prefix="/api")
app.include_router(document.router, prefix="/api")
app.include_router(references.router, prefix="/api")
app.include_router(terminology.router, prefix="/api")
app.include_router(baseline.router, prefix="/api")
app.include_router(export.router, prefix="/api")
app.include_router(import_review.router, prefix="/api")
app.include_router(workbook.router, prefix="/api")
app.include_router(block_router, prefix="/api")

app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")


@app.get("/")
def root() -> FileResponse:
    return FileResponse(_STATIC_INDEX)