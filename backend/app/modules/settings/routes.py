from fastapi import APIRouter

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/_health")
def settings_health() -> dict[str, str]:
    return {"module": "settings", "status": "ok"}
