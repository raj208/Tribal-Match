from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    debug=settings.app_debug,
    version="0.1.0",
    description="Tribal Match modular monolith API foundation",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

upload_dir = Path(settings.media_upload_dir)
upload_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(upload_dir)), name="uploads")


@app.get("/")
def root() -> dict[str, str]:
    return {
        "app": settings.app_name,
        "env": settings.app_env,
        "docs": "/docs",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "app": settings.app_name,
    }


app.include_router(api_router, prefix=settings.api_v1_prefix)