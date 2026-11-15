from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.routers import backups, document, health, knowledge, projects, technical, workspace

_STATIC_INDEX = Path(__file__).resolve().parent / "static" / "index.html"

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


@app.get("/")
def root() -> FileResponse:
    return FileResponse(_STATIC_INDEX)