from fastapi import APIRouter

router = APIRouter(prefix="/media", tags=["media"])


@router.get("/_health")
def media_health() -> dict[str, str]:
    return {"module": "media", "status": "ok"}
