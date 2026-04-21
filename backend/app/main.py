from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import urlsplit

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import settings
from app.db.migration_runner import run_database_migrations


def _is_local_database_url(database_url: str) -> bool:
    host = (urlsplit(database_url).hostname or "").strip().lower()
    return host in {"localhost", "127.0.0.1", "::1", "postgres"}


def _should_run_migrations_on_startup() -> bool:
    if settings.run_db_migrations_on_startup:
        return True

    return settings.app_env.strip().lower() == "development" and _is_local_database_url(settings.database_url)


@asynccontextmanager
async def lifespan(_: FastAPI):
    if _should_run_migrations_on_startup():
        run_database_migrations()
    yield

app = FastAPI(
    title=settings.app_name,
    debug=settings.app_debug,
    version="0.1.0",
    description="Tribal Match modular monolith API foundation",
    lifespan=lifespan,
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
