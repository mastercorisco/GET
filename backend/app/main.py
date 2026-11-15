from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.deps import get_settings
from app.routers import backups, health, workspace

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


@app.get("/")
def root() -> dict[str, str]:
    settings = get_settings()
    return {
        "name": "GET",
        "api": "/api/health",
        "host": settings.host,
    }