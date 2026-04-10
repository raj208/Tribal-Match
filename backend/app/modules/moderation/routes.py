from fastapi import APIRouter

router = APIRouter(prefix="/moderation", tags=["moderation"])


@router.get("/_health")
def moderation_health() -> dict[str, str]:
    return {"module": "moderation", "status": "ok"}
