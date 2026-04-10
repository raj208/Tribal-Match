from fastapi import APIRouter

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/_health")
def notifications_health() -> dict[str, str]:
    return {"module": "notifications", "status": "ok"}
