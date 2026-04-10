from fastapi import APIRouter

router = APIRouter(prefix="/profile", tags=["profiles"])


@router.get("/_health")
def profiles_health() -> dict[str, str]:
    return {"module": "profiles", "status": "ok"}
