from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(prefix="/meta", tags=["meta"])

MODULES = [
    {"name": "auth", "base_path": "/auth", "status": "ready"},
    {"name": "users", "base_path": "/users", "status": "ready"},
    {"name": "profiles", "base_path": "/profile", "status": "ready"},
    {"name": "media", "base_path": "/media", "status": "ready"},
    {"name": "discovery", "base_path": "/profiles", "status": "ready"},
    {"name": "interests", "base_path": "/interests", "status": "ready"},
    {"name": "verification", "base_path": "/verification", "status": "ready"},
    {"name": "moderation", "base_path": "/moderation", "status": "ready"},
    {"name": "settings", "base_path": "/settings", "status": "ready"},
    {"name": "notifications", "base_path": "/notifications", "status": "ready"},
]


@router.get("/health")
def api_health() -> dict[str, str]:
    return {
        "status": "ok",
        "app_name": settings.app_name,
        "env": settings.app_env,
        "api_prefix": settings.api_v1_prefix,
    }


@router.get("/modules")
def api_modules() -> dict[str, list[dict[str, str]]]:
    return {"modules": MODULES}